# 🧩 Pirambu Innovation — Backend

Api do Pirambu Innovation, desenvolvido com **Python + Flask**.  

Fornece uma API REST para visitar e gerenciar a página do [Pirambu Innovation(testes)](https://pirambuweb-testes.netlify.app/).


## Rodando localmente

Primeiro, clone o projeto
```bash
git clone https://github.com/Bebel132/Pirambu-Innovation-api.git
cd Pirambu-Innovation-api
```

Depois crie e acesse um ambiente virtual do python
```bash
python -m venv venv
./venv/Scripts/activate
```

E instale as dependências com o pip
```bash
pip install -r requirements.txt
```

Com isso, as dependências do flask já serão instaladas e será possível rodar a api
```bash
python app.py
```

## AJUSTE NO CORS

Para poder fazer requisições no front local, é necessário ajustar a regra de CORS que possibilita apenas do front no netlify fazer requisições: 

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
para:
```python
CORS(app, supports_credentials=True)