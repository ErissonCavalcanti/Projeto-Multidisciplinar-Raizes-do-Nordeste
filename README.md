# 🌵 API Raízes do Nordeste 

API backend para gestão de pedidos de delivery.

## 🚀 Tecnologias
- FastAPI
- SQLAlchemy
- JWT
- SQLite

## 🔐 Autenticação
Login com JWT.

Usuário padrão:
- Email: admin@email.com
- Senha: 123456

## 📦 Funcionalidades
- CRUD de produtos
- Criação de pedidos com itens
- Controle de estoque
- Atualização de status
- Filtro de pedidos
- Controle de acesso por perfil (ADMIN)

## ▶️ Como rodar

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload
