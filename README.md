# api_crud_senac


# Uvicorn
```
uvicorn main:app --reload
```

# Criando a venv e ativando
```bash
python -m venv venv
# later (Git Bash/Linux/Mac)
source ./venv/Scripts/activate
# if Windows CMD/PowerShell
.\venv\Scripts\activate
# install requirements
pip install -r requirements.txt
# save new requirements
pip freeze > requirements.txt
```

api_crud_senac/
├── main.py                 # Ponto de entrada (Program.cs no .NET)
├── requirements.txt        # Dependências (packages.config/.csproj)
├── .env                   # Variáveis de ambiente (appsettings.json)
├── README.md
├── venv/
└── app/                   # Pasta principal da aplicação
    ├── __init__.py
    ├── config.py          # Configurações (Startup.cs)
    ├── database.py        # Configuração do banco (DbContext)
    ├── dependencies.py    # Injeções de dependência
    ├── models/           # Modelos de dados (Models)
    │   ├── __init__.py
    │   ├── models.py     # Modelos SQLAlchemy
    │   └── schemas.py    # Modelos Pydantic (DTOs)
    ├── services/         # Lógica de negócio (Services)
    │   ├── __init__.py
    │   ├── user_service.py
    │   └── product_service.py
    ├── repositories/     # Acesso a dados (Repositories)
    │   ├── __init__.py
    │   ├── user_repository.py
    │   └── product_repository.py
    ├── routers/          # Controllers
    │   ├── __init__.py
    │   ├── users.py      # UserController
    │   └── products.py   # ProductController
    └── utils/            # Utilitários
        ├── __init__.py
        ├── auth.py       # Autenticação
        └── exceptions.py # Exception handlers