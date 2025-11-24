from fastapi import FastAPI
from os import getenv
from database.mongo_client import corridas_collection, criar_indices
from database.redis_client import redis_client, obter_saldo
from models.corrida_model import CorridaModel
from producer import connect_broker, publish_corrida_event

app = FastAPI(title=getenv("APP_NAME", "TransFlow Backend"))

broker = None 

@app.on_event("startup")
async def startup_event():
    global broker
    broker = await connect_broker()
    await criar_indices()
    print("[App] Aplicação iniciada com sucesso!")

@app.on_event("shutdown")
async def shutdown_event():
    print("Aplicação finalizando...")

@app.post("/corridas")
async def cadastrar_corrida(corrida: CorridaModel):
    """
    Cadastra uma nova corrida e publica um evento para o consumer processar.
    
    A corrida será registrada no MongoDB e o saldo do motorista será 
    atualizado de forma assíncrona através do RabbitMQ.
    """
    corrida_dict = corrida.dict()
    await publish_corrida_event(corrida_dict)
    return {
        "status": "Evento enviado para processamento",
        "id_corrida": corrida_dict.get("id_corrida"),
        "motorista": corrida_dict.get("motorista", {}).get("nome"),
        "valor_corrida": corrida_dict.get("valor_corrida")
    }

@app.get("/corridas")
async def listar_corridas():
    """
    Lista todas as corridas registradas no MongoDB.
    Retorna um array de corridas com seus dados completos.
    """
    docs = await corridas_collection.find().to_list(1000)
    # Remove _id (ObjectId não é serializável em JSON)
    return [{"id": str(doc.get("_id", "")), **{k: v for k, v in doc.items() if k != "_id"}} for doc in docs]

@app.get("/corridas/{forma_pagamento}")
async def filtrar_pagamento(forma_pagamento: str):
    """
    Filtra corridas por forma de pagamento.
    Retorna apenas as corridas que usaram a forma de pagamento especificada.
    """
    docs = await corridas_collection.find(
        {"forma_pagamento": forma_pagamento}
    ).to_list(1000)
    # Remove _id (ObjectId não é serializável em JSON)
    return [{"id": str(doc.get("_id", "")), **{k: v for k, v in doc.items() if k != "_id"}} for doc in docs]

@app.get("/saldo/{motorista}")
async def saldo_motorista(motorista: str):
    """
    Retorna o saldo atual de um motorista no Redis.
    
    O saldo é incrementado automaticamente quando uma corrida é processada
    pelo consumer através do RabbitMQ.
    
    Exemplo:
        GET /saldo/Carla%20Santos → {"motorista":"Carla Santos","saldo":50.0}
    """
    saldo = obter_saldo(motorista)
    return {"motorista": motorista, "saldo": saldo}


@app.post("/saldo/{motorista}")
async def inicializar_saldo_endpoint(motorista: str, valor: float = 0.0):
    """
    Inicializa ou reseta o saldo de um motorista (uso administrativo).
    
    Exemplo:
        POST /saldo/Carla%20Santos?valor=100
        Resultado: {"motorista":"Carla Santos","saldo_anterior":50.0,"saldo_novo":100.0}
    """
    from database.redis_client import inicializar_saldo as init_saldo
    saldo_anterior = obter_saldo(motorista)
    novo_saldo = init_saldo(motorista, valor)
    return {
        "motorista": motorista,
        "saldo_anterior": saldo_anterior,
        "saldo_novo": novo_saldo
    }

