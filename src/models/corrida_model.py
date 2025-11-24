from pydantic import BaseModel, Field
from typing import Optional

# Definição do modelo para os dados do Passageiro
class PassageiroModel(BaseModel):
    """
    Representa os dados do passageiro para a corrida.
    """
    nome: str = Field(..., description="O nome completo do passageiro.")
    telefone: str = Field(..., description="O número de telefone do passageiro.")

# Definição do modelo para os dados do Motorista
class MotoristaModel(BaseModel):
    """
    Representa os dados do motorista para a corrida.
    """
    nome: str = Field(..., description="O nome completo do motorista.")
    # A nota do motorista é opcional e deve estar entre 0.0 e 5.0
    nota: Optional[float] = Field(
        None, 
        description="A nota de avaliação do motorista (entre 0.0 e 5.0).",
        ge=0.0, # Maior ou igual a 0.0
        le=5.0  # Menor ou igual a 5.0
    )

# Definição do modelo principal para os dados da Corrida
class CorridaModel(BaseModel):
    """
    Modelo completo para os dados de uma corrida.
    """
    id_corrida: str = Field(..., description="Identificador único da corrida, ex: 'abc123'.")
    
    # Campos aninhados usando os modelos definidos acima
    passageiro: PassageiroModel = Field(..., description="Detalhes do passageiro.")
    motorista: MotoristaModel = Field(..., description="Detalhes do motorista.")
    
    origem: str = Field(..., description="Local de origem da corrida, ex: 'Centro'.")
    destino: str = Field(..., description="Local de destino da corrida, ex: 'Inoã'.")
    
    # O valor da corrida deve ser um número positivo
    valor_corrida: float = Field(..., description="Valor total da corrida.", gt=0.0)
    
    forma_pagamento: str = Field(..., description="Método de pagamento utilizado, ex: 'DigitalCoin'.")
    
    class Config:
        # Configuração para exemplos de schema/documentação (swagger)
        json_schema_extra = {
            "example": {
                "id_corrida": "abc123",
                "passageiro": {"nome": "João", "telefone": "99999-1111"},
                "motorista": {"nome": "Carla", "nota": 4.8},
                "origem": "Centro",
                "destino": "Inoã",
                "valor_corrida": 35.50,
                "forma_pagamento": "DigitalCoin"
            }
        }

if __name__ == "__main__":
    # Exemplo de como o modelo pode ser validado (apenas para demonstração)
    dados_exemplo = {
        "id_corrida": "exemplo_001",
        "passageiro": {"nome": "Ana Silva", "telefone": "98765-4321"},
        "motorista": {"nome": "Pedro Santos", "nota": 5.0},
        "origem": "Praça Central",
        "destino": "Aeroporto",
        "valor_corrida": 55.90,
        "forma_pagamento": "Cartão"
    }
    
    try:
        corrida = CorridaModel(**dados_exemplo)
        print("Modelo validado com sucesso:")
        print(corrida.model_dump_json(indent=2))
    except Exception as e:
        print(f"Erro de validação: {e}")