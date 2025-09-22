<div align="center">

# API CRUD SENAC

API RESTful construída com FastAPI, Pydantic e SQLAlchemy para operações de cadastro, consulta e gerenciamento de usuários, produtos, clientes, categorias e marcas.

</div>

## Sumário
- Visão geral
- Principais funcionalidades
- Arquitetura e pastas
- Requisitos
- Configuração e execução
- Banco de dados
- Documentação da API
- Convenções e qualidade de código
- Troubleshooting

## Visão geral
Este projeto fornece um backend moderno utilizando FastAPI, com validação via Pydantic e persistência de dados com SQLAlchemy. Inclui recursos de autenticação, gerenciamento de usuários, produtos (com categorias e marcas), e clientes.

## Principais funcionalidades
- CRUD de usuários, produtos e clientes.
- Categorias e marcas de produtos com soft delete e listagem somente de ativos.
- Filtros de busca por categoria, marca, texto e estoque baixo.
- Tratamento consistente de erros e respostas padronizadas.
- Documentação automática via Swagger (OpenAPI).

## Arquitetura e pastas
```
api_crud_senac/
├─ app/
│  ├─ controller/           # Rotas FastAPI
│  ├─ models/               # Pydantic + SQLAlchemy models
│  ├─ repositories/         # Acesso ao banco (ORM)
│  ├─ utils/                # Utilidades e modelos de erro
│  └─ database.py           # Sessão e Base SQLAlchemy
├─ crud_senac.db            # SQLite (desenvolvimento)
├─ main.py                  # Inicialização da aplicação FastAPI
├─ requirements.txt         # Dependências Python
└─ README.md
```

## Requisitos
- Python 3.11+ (recomendado 3.11/3.12/3.13)
- Pip
- SQLite para ambiente local (ou configure outro SGBD no `database.py`)

## Configuração e execução
1) Clonar o repositório
```bash
git clone <URL-DO-REPOSITORIO>
cd api_crud_senac
```

2) Criar e ativar ambiente virtual
```bash
python -m venv venv

# Windows PowerShell/CMD
.\venv\Scripts\activate

# Windows Git Bash
source ./venv/Scripts/activate

# Linux/MacOS
source venv/bin/activate
```

3) Instalar dependências
```bash
pip install -r requirements.txt
```

4) Executar a aplicação (desenvolvimento)
```bash
uvicorn main:app --reload
```

Aplicação disponível em `http://localhost:8000`.

## Banco de dados
- O projeto utiliza SQLite por padrão (arquivo `crud_senac.db`).
- As tabelas são criadas automaticamente no startup (`main.py`).
- Para outros bancos, ajuste o `engine`/`SessionLocal` em `app/database.py`.

## Documentação da API
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Principais endpoints (rotas podem variar conforme implementação):
- `GET /api/v1/products` — Lista produtos com filtros (categoria, marca, busca, low_stock)
- `POST /api/v1/products` — Cria produto
- `GET /api/v1/products/category` — Lista categorias ativas
- `POST /api/v1/products/category` — Cria categoria
- `PATCH /api/v1/products/category/{id}` — Atualiza nome de categoria
- `DELETE /api/v1/products/category/{id}` — Soft delete (desativa)
- `POST /api/v1/products/brand` — Cria marca
- Demais rotas: `users`, `auth`, `clientes`

O backend estará rodando em: **http://localhost:8000**

### 5. Documentação da API
- **FastApi/Swagger UI**: http://localhost:8000/docs


## Conta Admin

url: /api/v1/users/

```bash
{
  "email": "admin@teste.com",
  "nome": "Administrador",
  "telefone": "11999999999",
  "data_nascimento": "1990-01-01",
  "password": "senha123",
  "confirm_password": "senha123",
  "cpf": "12345678901",
  "role": "admin"
}
```
## Convenções e qualidade de código
- Padrão de respostas consistente com chaves: `success`, `message`, `data`, `timestamp` e códigos de erro (`code`) quando aplicável.

## Troubleshooting
- Erros de validação retornam HTTP 422 com detalhes do campo e mensagem.
- Certifique-se de ativar a `venv` correta antes de instalar dependências.
- Ao alterar a configuração do banco, remova/recrie o arquivo SQLite ou rode migrações adequadas.

---

Projeto de referência educacional para CRUD com FastAPI, Pydantic e SQLAlchemy.
