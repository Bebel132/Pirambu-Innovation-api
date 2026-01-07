# Pirambu Innovation — Backend

API do Pirambu Innovation, desenvolvida com **Python + Flask**.

Fornece uma API REST para visitar e gerenciar a página do https://pirambuweb.netlify.app/.

---

## Rodando localmente

Clone o projeto:

```bash
git clone https://github.com/Bebel132/Pirambu-Innovation-api.git
cd Pirambu-Innovation-api
```

Crie e ative um ambiente virtual:

```bash
python -m venv venv
./venv/Scripts/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute a API:

```bash
python app.py
```

---

## Ajuste no CORS

Para permitir requisições do front local, ajuste a regra de CORS.

Original:

```python
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": [
        "https://pirambuweb.netlify.app"
    ]}},
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Set-Cookie"]
)
```

Para desenvolvimento:

```python
CORS(app, supports_credentials=True)
```

---

## Arquitetura da Aplicação

A API segue uma arquitetura **RESTful** baseada em Flask, organizada em módulos por domínio (auth, users, courses, news, projects, events). Cada módulo possui rotas específicas para operações CRUD e gerenciamento de estados (ativar, desativar, publicar).

### Componentes principais:

- **Flask**: Framework principal para rotas e controle HTTP.
- **Swagger/OpenAPI**: Documentação interativa via `openapi.json`.
- **Banco de Dados**: Persistência dos dados (configuração depende do ambiente).
- **Middleware CORS**: Controle de acesso entre front e back.

### Fluxo geral:

1. O cliente (frontend) consome endpoints REST.
2. A API valida sessão via cookie (`session`) para rotas protegidas.
3. Operações CRUD são realizadas conforme os modelos definidos (User, Course, News, Projects, Events).

---

## Autenticação via Google OAuth

A autenticação é feita pelo **Google OAuth 2.0**:

- **/auth/login**: Redireciona para o Google para iniciar o fluxo.
- **/auth/callback**: Recebe o código do Google, valida e cria a sessão do usuário.
- **Sessão**: Um cookie `session` é definido para autenticar requisições subsequentes.
- **/auth/profile**: Retorna dados do usuário autenticado.

Esse fluxo garante login seguro e integração com contas Google, sem necessidade de senha local.
