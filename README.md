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

O servidor MCP sera iniciado a partir de `project/server.py` conforme as proximas issues implementarem as tools obrigatorias.

## Smoke test do banco

Para validar rapidamente a persistencia SQLite:

```powershell
.\.venv\Scripts\python.exe project\smoke_test.py
```

## Demo local

Para ver o fluxo atual na pratica com criacao de usuarios e busca semantica:

```powershell
.\.venv\Scripts\python.exe project\demo_local.py
```
