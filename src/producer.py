from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitMessage
import asyncio
from os import getenv

RABBIT_URL = getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")
broker = None
queue = None

async def connect_broker():
    global broker, queue
    if broker is not None:
        return broker

    while True:
        try:
            broker = RabbitBroker(RABBIT_URL)
            await broker.start()

            queue_name = "corrida_finalizada"
            queue = RabbitQueue(queue_name)
            await broker.declare_queue(queue)

            print("Conectou ao RabbitMQ e fila criada!")
            return broker
        except Exception as e:
            print(f"RabbitMQ indisponível ({e}), tentando novamente em 10s...")
            await asyncio.sleep(10)

async def publish_corrida_event(event: dict):
    """
    Publica um evento de corrida finalizada no RabbitMQ.
    
    O event deve conter os campos obrigatórios:
    - id_corrida
    - motorista (com nome e opcionalmente nota)
    - valor_corrida
    - forma_pagamento
    """
    broker = await connect_broker()
    global queue

    try:
        # Validação básica de campos obrigatórios
        required_fields = ["id_corrida", "motorista", "valor_corrida", "forma_pagamento"]
        missing = [f for f in required_fields if f not in event]
        if missing:
            raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing)}")

        # Validação de estrutura do motorista
        if not isinstance(event.get("motorista"), dict) or "nome" not in event["motorista"]:
            raise ValueError("Motorista deve ter um campo 'nome'")

        # Publica o dict direto (faststream serializa para JSON)
        await broker.publish(queue=queue, message=event)
        print(f"[→ RabbitMQ] Evento publicado: {event.get('id_corrida')} (R${event.get('valor_corrida', 0):.2f})")
        
    except Exception as e:
        print(f"[✗] Erro ao publicar evento: {type(e).__name__}: {e}")
        raise
