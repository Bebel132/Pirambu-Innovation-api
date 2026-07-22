# Pirambu Innovation — Backend

API REST desenvolvida em **Python + Flask** para o projeto **Pirambu Innovation**.

A API é responsável pelo gerenciamento de todo o conteúdo exibido no site, incluindo autenticação, gerenciamento de usuários autorizados, cursos, notícias, projetos, eventos, biografia e arquivos enviados pelos administradores.

---

## Funcionalidades

- Login via Google OAuth 2.0
- Controle de sessão utilizando cookies
- Controle de acesso por lista de usuários autorizados
- CRUD completo de:
  - Cursos
  - Notícias
  - Projetos
  - Eventos
  - Biografia
- Upload e gerenciamento de imagens
- Cache HTTP utilizando **Cache-Control**, **ETag** e **304 Not Modified**
- Rate Limiting para prevenção de abuso
- Headers HTTP de segurança
- Documentação automática da API utilizando Swagger (somente em desenvolvimento)

---

# Tecnologias

O projeto foi desenvolvido utilizando:

- Python 3
- Flask
- Flask-RESTX
- SQLAlchemy
- Flask-Migrate
- Flask-CORS
- Flask-Limiter
- SQLite
- Google OAuth 2.0

---

# Arquitetura

A API segue uma arquitetura modular.

Cada domínio da aplicação possui seu próprio conjunto de endpoints e regras de negócio, facilitando manutenção e evolução do projeto.

```
app.py
│
├── models/
│
├── migrations/
│
├── extensions.py
│
└── resourses/
    ├── Auth.py
    ├── Users.py
    ├── Courses.py
    ├── News.py
    ├── Projects.py
    ├── Events.py
    └── Biography.py
```

### Organização

### app.py

Responsável por inicializar toda a aplicação.

Nele são configurados:

- Flask
- SQLAlchemy
- Migrations
- CORS
- Swagger
- Rate Limiter
- Security Headers
- Registro dos Namespaces

---

### models/

Contém todos os modelos do banco de dados utilizados pela aplicação.

Cada entidade possui seu próprio modelo SQLAlchemy.

Exemplos:

- User
- AllowedUsers
- Course
- Project
- Event
- News
- Biography

---

### resourses/

Contém todos os endpoints da API.

Cada arquivo representa um módulo da aplicação e expõe apenas as rotas relacionadas ao seu domínio.

Exemplo:

```
Courses
    GET
    POST
    PUT
    DELETE

Projects
    GET
    POST
    PUT
    DELETE
```

---

### decorators/

Contém decorators reutilizáveis utilizados em diferentes partes da aplicação.

Atualmente:

- login_required
- limiter

---

# Fluxo de autenticação

O sistema utiliza **Google OAuth 2.0**.

Fluxo simplificado:

```
Frontend

      │

      ▼

/auth/login

      │

      ▼

Google

      │

      ▼

/auth/callback

      │

      ▼

Sessão criada

      │

      ▼

Rotas protegidas
```

Após a autenticação, a API cria uma sessão utilizando cookies.

Todos os endpoints administrativos verificam:

- existência da sessão;
- existência do usuário;
- existência do usuário na lista de usuários autorizados.

Caso qualquer uma dessas verificações falhe, o acesso é negado.

---

# Cache HTTP

Os arquivos enviados para a aplicação (imagens de cursos, notícias, projetos, eventos e biografia) são disponibilizados através de endpoints específicos.

Esses endpoints implementam:

- Cache-Control
- ETag
- 304 Not Modified

Com isso, o navegador passa a controlar automaticamente o cache das imagens, evitando downloads desnecessários e reduzindo significativamente o tempo de carregamento da aplicação.

---

# Segurança

A API utiliza diversas camadas de proteção.

## Cookies

- HttpOnly
- Secure (produção)
- SameSite configurado conforme o ambiente

---

## Rate Limiting

As rotas administrativas possuem limite de requisições utilizando **Flask-Limiter**, reduzindo tentativas de abuso.

---

## Security Headers

Todas as respostas incluem cabeçalhos como:

- Strict-Transport-Security
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy
- Content-Security-Policy
- Cross-Origin-Resource-Policy

---

## CORS

O acesso é permitido apenas para:

- https://pirambuweb.netlify.app

Durante o desenvolvimento local, basta adicionar o endereço do frontend às origens permitidas.

---

# Rodando localmente

Clone o projeto:

```bash
git clone https://github.com/Bebel132/Pirambu-Innovation-api.git

cd Pirambu-Innovation-api
```

Crie o ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente.

Windows

```bash
venv\Scripts\activate
```

Linux

```bash
source venv/bin/activate
```

Instale as dependências.

```bash
pip install -r requirements.txt
```

Configure o arquivo `.env`.

Exemplo:

```env
ENV=development

SECRET_KEY=

DATABASE_URL=

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
REDIRECT_URI=

MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
MICROSOFT_REDIRECT_URI=

FRONTEND_POST_LOGIN_URL=
```

Execute a aplicação.

```bash
python app.py
```

---

# Desenvolvimento

Durante o desenvolvimento:

- Swagger permanece habilitado;
- cookies Secure são desativados;
- SameSite utiliza `Lax`;
- é possível utilizar SQLite localmente.

Em produção:

- Swagger é desabilitado;
- cookies Secure são obrigatórios;
- Security Headers permanecem ativos;
- Rate Limiting permanece ativo.

---

# Deploy

O ambiente de produção atualmente utiliza:

- API hospedada em um dispositivo Android
- Termux
- tmux
- OpenSSH
- Cloudflare Tunnel

Essa arquitetura elimina a necessidade de um VPS para este projeto e permite manter a aplicação disponível continuamente utilizando hardware reaproveitado.

---
