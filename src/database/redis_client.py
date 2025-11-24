import redis
from os import getenv

REDIS_HOST = getenv("REDIS_HOST", "redis")
REDIS_PORT = int(getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def adicionar_saldo(motorista: str, valor: float) -> float:
    """
    Adiciona um valor ao saldo do motorista de forma atômica.
    Retorna o novo saldo total.
    
    Args:
        motorista: Nome do motorista (será convertido para lowercase)
        valor: Valor a adicionar ao saldo
        
    Returns:
        float: Novo saldo total do motorista
    """
    chave = f"saldo:{motorista.lower()}"
    novo_saldo = redis_client.incrbyfloat(chave, valor)
    return float(novo_saldo)


def obter_saldo(motorista: str) -> float:
    """
    Obtém o saldo atual do motorista.
    
    Args:
        motorista: Nome do motorista (será convertido para lowercase)
        
    Returns:
        float: Saldo atual do motorista (0.0 se não existir)
    """
    chave = f"saldo:{motorista.lower()}"
    saldo = redis_client.get(chave)
    return float(saldo) if saldo else 0.0


def inicializar_saldo(motorista: str, valor_inicial: float = 0.0) -> float:
    """
    Inicializa ou reseta o saldo de um motorista.
    
    Args:
        motorista: Nome do motorista (será convertido para lowercase)
        valor_inicial: Valor inicial do saldo (padrão: 0.0)
        
    Returns:
        float: Saldo configurado
    """
    chave = f"saldo:{motorista.lower()}"
    redis_client.set(chave, valor_inicial)
    return float(valor_inicial)