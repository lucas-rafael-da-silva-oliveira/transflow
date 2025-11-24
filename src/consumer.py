import asyncio
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from os import getenv
from database.redis_client import adicionar_saldo
from database.mongo_client import corridas_collection
import aio_pika

RABBIT_URL = getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")

# Cria o broker
broker = RabbitBroker(RABBIT_URL)
app = FastStream(broker)

@app.on_startup
async def startup():
    print("[Consumer] Conectando ao RabbitMQ...")

@broker.subscriber("corrida_finalizada")
async def processar_corrida(event: dict):
    """
    Processa um evento de corrida finalizada:
    1. Atualiza o saldo do motorista no Redis (atômico)
    2. Registra a corrida no MongoDB (idempotente com upsert)
    """
    try:
        motorista_nome = event["motorista"]["nome"]
        valor_corrida = float(event["valor_corrida"])
        id_corrida = event.get("id_corrida", "desconhecido")

        # Atualiza saldo do motorista no Redis (atômico via INCRBYFLOAT)
        novo_saldo = adicionar_saldo(motorista_nome, valor_corrida)
        print(f"[✓ Redis] Saldo de '{motorista_nome}' atualizado: +R${valor_corrida:.2f} → Total: R${novo_saldo:.2f}")

        # Insere/atualiza documento no MongoDB (idempotente com upsert)
        result = await corridas_collection.update_one(
            {"id_corrida": id_corrida},
            {"$set": event},
            upsert=True
        )
        
        if result.upserted_id:
            print(f"[✓ MongoDB] Nova corrida registrada: {id_corrida}")
        else:
            print(f"[✓ MongoDB] Corrida atualizada: {id_corrida}")

        print(f"[✔] Corrida processada com sucesso: {id_corrida}\n")

    except KeyError as e:
        print(f"[✗] Erro: campo obrigatório ausente no evento: {e}")
    except ValueError as e:
        print(f"[✗] Erro: tipo de dado inválido: {e}")
    except Exception as e:
        print(f"[✗] Erro ao processar corrida: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("[Consumer] Aguardando eventos da fila 'corrida_finalizada'...\n")
    # Use asyncio.run to properly run the async app
    import asyncio
    asyncio.run(app.run())
