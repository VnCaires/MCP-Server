# Servidor MCP com Persistencia e Busca Vetorial

Implementacao do case tecnico para um servidor MCP capaz de:
- criar usuarios
- armazenar dados em SQLite
- gerar embeddings locais
- indexar vetores em FAISS
- executar busca semantica via tools MCP

## Escopo atual

O servidor ja possui as tools obrigatorias do case:
- `create_user`
- `search_users`
- `get_user`

Diferencial opcional ja implementado:
- `list_users`

## Estrutura

```text
project/
|-- server.py
|-- database.py
|-- embeddings.py
|-- vector_store.py
|-- models.py
|-- errors.py
`-- faiss_index/
```

## Pre-requisitos

- Python 3.13+
- Windows PowerShell ou terminal compativel

## Instalacao

### 1. Criar e ativar a venv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Executar o servidor MCP

```powershell
.\.venv\Scripts\python.exe project\server.py
```

## Executar a suite de testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Exemplos de uso das tools MCP

### `create_user`

Entrada:

```json
{
  "name": "Ana Souza",
  "email": "ana@example.com",
  "description": "Cliente interessada em automacao financeira e atendimento premium"
}
```

Resposta esperada:

```json
{
  "id": 1
}
```

### `search_users`

Entrada:

```json
{
  "query": "automacao financeira premium",
  "top_k": 3
}
```

Resposta esperada:

```json
[
  {
    "id": 1,
    "name": "Ana Souza",
    "email": "ana@example.com",
    "description": "Cliente interessada em automacao financeira e atendimento premium",
    "score": 0.91
  }
]
```

### `get_user`

Entrada:

```json
{
  "user_id": 1
}
```

Resposta esperada:

```json
{
  "id": 1,
  "name": "Ana Souza",
  "email": "ana@example.com",
  "description": "Cliente interessada em automacao financeira e atendimento premium"
}
```

## Persistencia local

O projeto usa:
- SQLite em `project/crm.sqlite3`
- FAISS em `project/faiss_index/users.index`
- mapeamento `vector_id -> user_id` em `project/faiss_index/metadata.json`

## Validacoes e erros

As tools retornam erros consistentes no formato:

```json
{
  "code": "validation_error | not_found | storage_error | embedding_error",
  "message": "..."
}
```

## Observacoes

- Os embeddings atuais sao locais e deterministicos, pensados para desenvolvimento e demonstracao
- A arquitetura foi mantida modular para facilitar troca futura do provedor de embeddings ou da estrategia vetorial
- O banco SQLite e os arquivos do indice FAISS sao criados automaticamente na primeira execucao
