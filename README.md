##  Configuração do Backend

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd api_crud_senac
```

### 2. Criar e ativar ambiente virtual
```bash
# Criar venv
python -m venv venv

# Ativar venv
# Windows (CMD/PowerShell)
.\venv\Scripts\activate

# Windows (Git Bash)
source ./venv/Scripts/activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Executar o servidor
```bash
uvicorn main:app --reload
```

O backend estará rodando em: **http://localhost:8000**

### 5. Documentação da API
- **FastApi/Swagger UI**: http://localhost:8000/docs


> Projeto desenvolvido para fins de estudo e demonstração de CRUD com FastAPI.