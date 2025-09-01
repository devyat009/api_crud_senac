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
.\venv\Scripts\activate && pip install -r requirements.txt

# Windows (Git Bash)
source ./venv/Scripts/activate && uvicorn main:app --reload

# Linux/Mac
source venv/bin/activate
```

### 3. Executar o servidor
```bash
uvicorn main:app --reload
```

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
> Projeto desenvolvido para fins de estudo e demonstração de CRUD com FastAPI.