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

## ▶️ Como rodar o projeto

### 1. Criar ambiente virtual
```bash
python -m venv .venv
2. Criar ambiente virtual
bashpython -m venv .venv
3. Ativar ambiente virtual
Windows:
bash.venv\Scripts\activate
Linux/Mac:
bashsource .venv/bin/activate
4. Instalar dependências
bashpip install -r requirements.txt
5. Rodar a API
bashuvicorn src.api.main:app --reload

📄 Documentação (Swagger)
Com a API rodando, acesse a documentação interativa no navegador:
http://127.0.0.1:8000/docs
Ou a documentação alternativa (ReDoc):
http://127.0.0.1:8000/redoc
