# Pirambu Innovation — Backend

API do Pirambu Innovation, desenvolvida com **Python + Flask**.

Fornece uma API REST para visitar e gerenciar a página do https://pirambuweb-testes.netlify.app/.

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
        "https://pirambuweb-testes.netlify.app"
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
- **Blueprints**: Separação lógica por domínio.
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

---

## Documentação da API

### BasePath: /

**Content-Type:** `application/json`

**Autenticação:** Cookie de sessão (`session`) via Google OAuth.

---

### Autenticação

- `GET /auth/login` → Redireciona para login Google.
- `GET /auth/callback` → Callback OAuth, define sessão.
- `POST /auth/logout` → Logout do usuário.
- `GET /auth/profile` → Perfil do usuário autenticado.

---

### Usuários

- `GET /users/` → Lista usuários.
- `POST /users/allowedUsers/` → Adiciona usuário permitido.
- `GET /users/allowedUsers/` → Lista usuários permitidos.
- `DELETE /users/allowedUsers/{id}` → Remove usuário permitido.

---

### Cursos

- `POST /courses/` → Cria curso.
- `GET /courses/` → Lista cursos.
- `GET /courses/{id}` → Detalha curso.
- `PUT /courses/{id}` → Atualiza curso.
- `DELETE /courses/{id}` → Remove curso.
- `POST /courses/activate/{id}` → Ativa curso.
- `POST /courses/deactivate/{id}` → Desativa curso.
- `GET /courses/deactivated` → Lista cursos desativados.
- `POST /courses/publish/{id}` → Publica curso.
- `GET /courses/published` → Lista cursos publicados.
- `GET /courses/{id}/file` → Obtém arquivo do curso.
- `POST /courses/{id}/upload` → Upload de arquivo (multipart/form-data).

---

### Notícias

CRUD + ativar/desativar/publicar + upload de arquivo:

- `POST /news/` | `GET /news/` | `GET /news/{id}` | `PUT /news/{id}` | `DELETE /news/{id}`
- `POST /news/activate/{id}` | `POST /news/deactivate/{id}` | `GET /news/deactivated`
- `POST /news/publish/{id}` | `GET /news/published`
- `GET /news/{id}/file` | `POST /news/{id}/upload`

---

### Projetos

Mesma estrutura de notícias:

- `POST /projects/` | `GET /projects/` | `GET /projects/{id}` | `PUT /projects/{id}` | `DELETE /projects/{id}`
- `POST /projects/activate/{id}` | `POST /projects/deactivate/{id}` | `GET /projects/deactivated`
- `POST /projects/publish/{id}` | `GET /projects/published`
- `GET /projects/{id}/file` | `POST /projects/{id}/upload`

---

### Eventos

Mesma estrutura de projetos:

- `POST /events/` | `GET /events/` | `GET /events/{id}` | `PUT /events/{id}` | `DELETE /events/{id}`
- `POST /events/activate/{id}` | `POST /events/deactivate/{id}` | `GET /events/deactivated`
- `POST /events/publish/{id}` | `GET /events/published`
- `GET /events/{id}/file` | `POST /events/{id}/upload`

---

### Teste

- `GET /teste` → Endpoint de teste.

---

## Modelos principais

- **User:** `{ email: string }`
- **Course:** `{ id, title, description, start_date, end_date, hasFile, is_draft, created_at }`
- **News / Projects / Events:** `{ id, title, description, hasFile, is_draft, created_at }`

---
