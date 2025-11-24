Universidade de Vassouras Campus Maricá
Engenharia de Software
Banco de Dados Não Relacionais
Professor Fabrício Dias
Estudante Lucas Rafael da Silva Oliveira

TRANSFLOW - SISTEMA DE GERENCIAMENTO DE CORRIDAS

---

RESUMO DA TAREFA

TransFlow é um sistema backend para gerenciamento de corridas com processamento assíncrono.
O projeto implementa 4 requisitos principais:

1. Cadastro e consulta de corridas em MongoDB (2.0 pontos)
2. Controle de saldo de motoristas em Redis com operações atômicas (2.0 pontos)
3. Processamento assíncrono de eventos via RabbitMQ com FastStream (3.0 pontos)
4. Containerização com Docker Compose e documentação (1.0 ponto)

Total: 8.0 pontos

---

COMO EXECUTAR O PROGRAMA

Pré-requisitos:
- Docker e Docker Compose instalados
- Acesso ao terminal/PowerShell

Passos:

1. Abra o terminal na pasta do projeto:
   cd "C:\Users\Lucas Rafael\Desktop\202514902 LUCAS RAFAEL DA SILVA OLIVEIRA P2 BD NÃO RELACIONAIS\transflow"

2. Inicie todos os serviços:
   docker compose up --build

3. Aguarde cerca de 30 segundos até aparecer "FastStream app started successfully"

4. O sistema estará pronto para uso:
   - API: http://localhost:8000
   - Swagger/Documentação: http://localhost:8000/docs
   - RabbitMQ Management: http://localhost:15672 (usuário: guest, senha: guest)

---

COMO TESTAR OS REQUISITOS

REQUISITO 1: Cadastro e Consulta de Corridas

Teste 1.1 - Criar uma corrida:

Abra o PowerShell e execute:

$event = @{
    id_corrida = "corrida-001"
    passageiro = @{ nome = "João Silva"; telefone = "11987654321" }
    motorista = @{ nome = "Maria Santos"; nota = 4.8 }
    origem = "Avenida Paulista"
    destino = "Centro"
    valor_corrida = 45.50
    forma_pagamento = "credito"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/corridas" -Method POST -Body $event -ContentType "application/json"

Resultado esperado: HTTP 200 com status "Evento enviado para processamento"


Teste 1.2 - Listar todas as corridas:

Invoke-WebRequest -Uri "http://localhost:8000/corridas" -Method GET | Select -ExpandProperty Content | ConvertFrom-Json

Resultado esperado: Lista com as corridas cadastradas em formato JSON


Teste 1.3 - Filtrar corridas por forma de pagamento:

Invoke-WebRequest -Uri "http://localhost:8000/corridas/credito" -Method GET | Select -ExpandProperty Content | ConvertFrom-Json

Resultado esperado: Apenas corridas com forma_pagamento = "credito"


---

REQUISITO 2: Controle de Saldo em Redis

Teste 2.1 - Inicializar saldo de um motorista:

Invoke-WebRequest -Uri "http://localhost:8000/saldo/Maria%20Santos?valor=100" -Method POST

Resultado esperado: HTTP 200 com {"motorista": "Maria Santos", "saldo": 100.0}


Teste 2.2 - Consultar saldo:

Invoke-WebRequest -Uri "http://localhost:8000/saldo/Maria%20Santos" -Method GET | Select -ExpandProperty Content | ConvertFrom-Json

Resultado esperado: {"motorista": "Maria Santos", "saldo": 100.0}


Teste 2.3 - Verificar atualização de saldo após corrida:

Antes de fazer este teste, execute o Teste 1.1 para criar uma corrida.

Aguarde 2 segundos para o processamento assíncrono.

Depois consulte o saldo:

Invoke-WebRequest -Uri "http://localhost:8000/saldo/Maria%20Santos" -Method GET | Select -ExpandProperty Content | ConvertFrom-Json

Resultado esperado: 
O saldo deve ter aumentado de 100.0 para 145.50 (100 + 45.50 da corrida)

Isso comprova que:
- A corrida foi publicada no RabbitMQ
- O consumer recebeu e processou o evento
- Redis foi atualizado com operação atômica (INCRBYFLOAT)

CONSULTAS VIA REDIS

COM O DOCKER RODANDO EM UM TERMINAL
ABRA outro e consulte "docker exec -it redis redis-cli"
Altere o saldo de Carla e João

SET saldo:Carla 100
SET saldo:Joao 200

Para a operação de consulta
use
GET saldo:Carla
GET saldo:Joao

---

REQUISITO 3: Processamento Assíncrono com RabbitMQ

Teste 3.1 - Publicação e processamento de evento:

1. Inicialize um saldo:
   Invoke-WebRequest -Uri "http://localhost:8000/saldo/Pedro%20Costa?valor=200" -Method POST

2. Crie uma corrida:
   $event = @{
       id_corrida = "corrida-async-001"
       passageiro = @{ nome = "Cliente"; telefone = "123456" }
       motorista = @{ nome = "Pedro Costa"; nota = 4.9 }
       origem = "Local A"
       destino = "Local B"
       valor_corrida = 60.00
       forma_pagamento = "pix"
   } | ConvertTo-Json

   Invoke-WebRequest -Uri "http://localhost:8000/corridas" -Method POST -Body $event -ContentType "application/json"

3. Aguarde 2 segundos

4. Verifique o saldo:
   Invoke-WebRequest -Uri "http://localhost:8000/saldo/Pedro%20Costa" -Method GET | Select -ExpandProperty Content | ConvertFrom-Json

   Resultado esperado: saldo = 260.00 (200 + 60)

5. Verifique se a corrida foi salva no MongoDB:
   Invoke-WebRequest -Uri "http://localhost:8000/corridas" -Method GET | Select -ExpandProperty Content | ConvertFrom-Json

   Resultado esperado: Corrida com id_corrida "corrida-async-001" deve estar listada


Teste 3.2 - Múltiplas corridas simultâneas (teste de atomicidade):

1. Inicialize saldo:
   Invoke-WebRequest -Uri "http://localhost:8000/saldo/Ana%20Paula?valor=500" -Method POST

2. Crie 3 corridas em sequência rápida:

   $corrida1 = @{
       id_corrida = "corrida-multi-1"
       passageiro = @{ nome = "Cliente 1"; telefone = "111111" }
       motorista = @{ nome = "Ana Paula"; nota = 4.7 }
       origem = "Ponto A"
       destino = "Ponto B"
       valor_corrida = 25.00
       forma_pagamento = "credito"
   } | ConvertTo-Json
   Invoke-WebRequest -Uri "http://localhost:8000/corridas" -Method POST -Body $corrida1 -ContentType "application/json"

   $corrida2 = @{
       id_corrida = "corrida-multi-2"
       passageiro = @{ nome = "Cliente 2"; telefone = "222222" }
       motorista = @{ nome = "Ana Paula"; nota = 4.7 }
       origem = "Ponto C"
       destino = "Ponto D"
       valor_corrida = 35.00
       forma_pagamento = "pix"
   } | ConvertTo-Json
   Invoke-WebRequest -Uri "http://localhost:8000/corridas" -Method POST -Body $corrida2 -ContentType "application/json"

   $corrida3 = @{
       id_corrida = "corrida-multi-3"
       passageiro = @{ nome = "Cliente 3"; telefone = "333333" }
       motorista = @{ nome = "Ana Paula"; nota = 4.7 }
       origem = "Ponto E"
       destino = "Ponto F"
       valor_corrida = 40.00
       forma_pagamento = "dinheiro"
   } | ConvertTo-Json
   Invoke-WebRequest -Uri "http://localhost:8000/corridas" -Method POST -Body $corrida3 -ContentType "application/json"

3. Aguarde 3 segundos para processamento:
   Start-Sleep -Seconds 3

4. Verifique o saldo final:
   Invoke-WebRequest -Uri "http://localhost:8000/saldo/Ana%20Paula" -Method GET | Select -ExpandProperty Content | ConvertFrom-Json

   Resultado esperado: saldo = 600.00 (500 + 25 + 35 + 40)

   Se o saldo estiver correto, isso comprova:
   - Todos os 3 eventos foram publicados no RabbitMQ
   - O consumer processou todos atomicamente
   - Não houve race conditions (operações conflitantes)
   - Os dados estão corretos


---

REQUISITO 4: Docker e Documentação

Verificação:

1. Todos os 5 containers devem estar rodando:
   docker ps

   Esperado ver:
   - transflow-app (porta 8000)
   - transflow-consumer (sem porta)
   - transflow-mongo (porta 27017)
   - transflow-redis (porta 6379)
   - transflow-rabbitmq (portas 5672, 15672)

2. Acesse a documentação da API:
   http://localhost:8000/docs

   Você verá o Swagger UI com todos os endpoints documentados


---

PARAR OS SERVIÇOS

Para encerrar o sistema:

docker compose down

Para encerrar e remover dados:

docker compose down --volumes

---

ESTRUTURA DO PROJETO

transflow/
├── src/
│   ├── main.py                 (API REST - endpoints)
│   ├── producer.py             (Publicador de eventos no RabbitMQ)
│   ├── consumer.py             (Processador assíncrono de eventos)
│   ├── database/
│   │   ├── mongo_client.py     (Conexão MongoDB)
│   │   └── redis_client.py     (Operações Redis)
│   └── models/
│       └── corrida_model.py    (Validação de dados com Pydantic)
├── docker-compose.yml          (Configuração dos 5 serviços)
├── dockerfile                  (Imagem da aplicação)
├── requirements.txt            (Dependências Python)
├── .env                        (Variáveis de ambiente)
├── README.md                   (Este arquivo)
└── testes/                     (Testes e validações anteriores)

---

ENDPOINTS DISPONÍVEIS

POST /corridas
Criar uma nova corrida
Request:
{
  "id_corrida": "string",
  "passageiro": {"nome": "string", "telefone": "string"},
  "motorista": {"nome": "string", "nota": float},
  "origem": "string",
  "destino": "string",
  "valor_corrida": float,
  "forma_pagamento": "string"
}
Response: 200 OK


GET /corridas
Listar todas as corridas
Response: 200 OK - Array de corridas


GET /corridas/{forma_pagamento}
Filtrar corridas por forma de pagamento
Response: 200 OK - Array filtrado


GET /saldo/{motorista}
Consultar saldo de um motorista
Response: 200 OK - {"motorista": "string", "saldo": float}


POST /saldo/{motorista}?valor=X
Inicializar saldo de um motorista
Response: 200 OK - {"motorista": "string", "saldo": float}


---

TECNOLOGIAS UTILIZADAS

FastAPI 0.121.3: Framework REST API
FastStream 0.6.3: Abstração para message brokers
RabbitMQ 3: Message broker para eventos assíncronos
MongoDB 7: Banco de dados NoSQL para corridas
Redis 7: Cache para saldos de motoristas
Motor 3.7.1: Driver assíncrono MongoDB
Pydantic 2.12.4: Validação de dados
Python 3.10+: Runtime
Docker e Docker Compose: Containerização

---

OPERAÇÕES DE BANCO DE DADOS

Redis:
- INCRBYFLOAT: Operação atômica para incrementar saldo
- GET: Consultar saldo
- SET: Inicializar saldo


MongoDB:
- update_one com upsert=True: Inserir ou atualizar corrida (garante idempotência)
- find: Listar corridas
- Indices: Criados na inicialização para performance (id_corrida único, forma_pagamento, motorista.nome)
