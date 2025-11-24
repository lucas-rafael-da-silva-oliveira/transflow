from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv

MONGO_URI = getenv("MONGO_URI")
MONGO_DB = getenv("MONGO_DB", "transflow")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]

corridas_collection = db["corridas"]


async def criar_indices():
    """
    Cria índices no MongoDB para melhorar eficiência de queries.
    """
    try:
        # Índice único em id_corrida para evitar duplicatas
        await corridas_collection.create_index(
            "id_corrida",
            unique=True,
            name="idx_id_corrida"
        )
        
        # Índice em forma_pagamento para filtros rápidos
        await corridas_collection.create_index(
            "forma_pagamento",
            name="idx_forma_pagamento"
        )
        
        # Índice em motorista.nome para buscas por motorista
        await corridas_collection.create_index(
            "motorista.nome",
            name="idx_motorista_nome"
        )
        
        print("[MongoDB] Índices criados com sucesso!")
    except Exception as e:
        print(f"[MongoDB] Erro ao criar índices: {e}")