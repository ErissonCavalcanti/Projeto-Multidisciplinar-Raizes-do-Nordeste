# API Raízes do Nordeste 

API backend para gestão de pedidos da Rede Raízes de Restaurantes do Nordeste, foi desenvolvida com FastAPI.  
O sistema permite controle de produtos, pedidos, estoque e autenticação segura com JWT.

---

## 🚀 Tecnologias

- FastAPI
- SQLAlchemy
- SQLite
- JWT (JSON Web Token)
- Pydantic

---

## 🔐 Autenticação

A API utiliza autenticação via JWT.

### 👤 Usuário padrão (seed automático)

- Email: admin@email.com  
- Senha: 123456  

---

## 📦 Funcionalidades

- ✔ CRUD completo de produtos
- ✔ Criação de pedidos com múltiplos itens
- ✔ Cálculo automático do valor total
- ✔ Controle de estoque com validação
- ✔ Atualização de status do pedido
- ✔ Fluxo de status:
  - AGUARDANDO_PAGAMENTO
  - RECEBIDO
  - EM_PREPARO
  - PRONTO
  - ENTREGUE
- ✔ Filtro de pedidos por status e canal
- ✔ Controle de acesso por perfil (ADMIN)
- ✔ Logs simples de operações

---

## 🔗 Endpoints principais

| Método | Rota | Descrição |
|------|------|---------|
| POST | /auth/login | Login e geração de token |
| GET | /produtos | Listar produtos |
| POST | /produtos | Criar produto (ADMIN) |
| POST | /pedidos | Criar pedido |
| GET | /pedidos | Listar pedidos |
| PATCH | /pedidos/{id}/status | Atualizar status |

---

▶️ Como Executar o Projeto:


1️⃣ Clonar o repositório

git clone: https://github.com/ErissonCavalcanti/Projeto-Multidisciplinar-Raizes-do-Nordeste

cd Projeto-Multidisciplinar-Raizes-do-Nordeste

---

2️⃣ Criar ambiente virtual
python -m venv .venv

---

3️⃣ Ativar ambiente virtual

Windows:

.venv\Scripts\activate

Linux / Mac:

source .venv/bin/activate

---

4️⃣ Instalar dependências
pip install -r requirements.txt

---

5️⃣ Configurar variáveis de ambiente

Crie um arquivo .env baseado no .env.example 
Exemplo:

DATABASE_URL=sqlite:///./database.db
SECRET_KEY=sua_chave_secreta

--- 

6️⃣ Criar usuário ADMIN (opcional)
python seed.py

👤 Usuário padrão
Email: admin@email.com

Senha: 123456

--- 

7️⃣ Executar a API

uvicorn src.api.main:app --reload

---

📄 Acessar documentação

Após iniciar o servidor:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

---

👨‍💻 Autor

Erisson josé cavalcanti da Silva

RU: 4628196

GitHub: https://github.com/ErissonCavalcanti
