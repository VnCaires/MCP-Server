# Servidor MCP com Persistencia e Busca Vetorial

Implementacao do case tecnico para um servidor MCP capaz de criar usuarios, armazenar dados em SQLite e executar busca semantica com FAISS.

## Estrutura

```text
project/
|-- server.py
|-- database.py
|-- embeddings.py
|-- vector_store.py
|-- models.py
`-- faiss_index/
```

## Setup com venv

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Executar

Suba o servidor MCP com:

```powershell
.\.venv\Scripts\python.exe project\server.py
```

No estado atual, o servidor registra as tools:
- `create_user`
- `search_users`
- `get_user`

## Demo local

Para ver o fluxo atual na pratica com criacao de usuarios e busca semantica:

```powershell
.\.venv\Scripts\python.exe project\demo_local.py
```
