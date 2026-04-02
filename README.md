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
- `Dockerfile`
- logging estruturado
- testes automatizados

## Estrutura

```text
project/
|-- server.py
|-- database.py
|-- embeddings.py
|-- logging_utils.py
|-- vector_store.py
|-- models.py
|-- errors.py
`-- faiss_index/
```

## Pre-requisitos

- Python 3.13+

## instalar e executar sem Docker

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
.\.venv\Scripts\python.exe -m project.server
```

Tambem funciona com:

```powershell
.\.venv\Scripts\python.exe project\server.py
```

## Executar com Docker (caso tenha instalado na máquina)

### 1. Build da imagem

```powershell
docker build -t mcp-server .
```

### 2. Rodar o servidor no container

```powershell
docker run --rm mcp-server
```

Observacao:
- O banco SQLite e os arquivos do indice FAISS serao criados dentro do container na primeira execucao
- Se quiser preservar esses arquivos entre execucoes, basta montar um volume depois

## Executar a suite de testes

### Sem o Docker
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### Com o Docker
```powershell
docker run --rm mcp-server python -m unittest discover -s tests -v
```

## Exemplos de uso das tools MCP

A seguir estão exemplos simples de como interagir com as principais ferramentas do servidor MCP.

### `create_user`
Cria um novo usuário com informações básicas e uma descrição contextual.

**Entrada:**

````markdown
```json
{
  "name": "Ana Souza",
  "email": "ana@example.com",
  "description": "Cliente interessada em automacao financeira e atendimento premium"
}
````

**Resposta esperada:**

```json
{
  "id": 1
}
```

---

### `search_users`

Realiza uma busca semantica por usuarios com base em uma consulta textual.

**Entrada:**

```json
{
  "query": "automacao financeira premium",
  "top_k": 3
}
```

**Resposta esperada:**

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

---

### `get_user`

Recupera os dados completos de um usuario a partir do seu ID.

**Entrada:**

```json
{
  "user_id": 1
}
```

**Resposta esperada:**

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

Validacoes adicionais de email aplicadas em `create_user`:
- espacos em volta do email sao removidos antes da validacao
- o email e normalizado para minusculas antes de persistir
- aliases com `+` no local-part sao rejeitados

Na pratica, isso evita duplicidades por caixa alta e mantem uma politica simples para identificacao unica de usuarios.

## Observabilidade

O servidor agora emite logs estruturados em JSON para os eventos principais:
- bootstrap e inicializacao do runtime
- inicio e fim de cada tool MCP
- falhas com `error_code` e `duration_ms`

Os logs sao emitidos em `stderr`, enquanto o transporte MCP continua em `stdio`.

Exemplo de log:

```json
{
  "level": "INFO",
  "logger": "project.server",
  "message": "create_user completed.",
  "event": "tool.invocation.completed",
  "context": {
    "tool_name": "create_user",
    "duration_ms": 12.418,
    "email_domain": "example.com",
    "created_user_id": 1
  }
}
```

## Observacoes

- Os embeddings atuais sao locais e deterministicos, pensados para desenvolvimento e demonstracao
- A arquitetura foi mantida modular para facilitar troca futura do provedor de embeddings ou da estrategia vetorial
- O banco SQLite e os arquivos do indice FAISS sao criados automaticamente na primeira execucao


