from dotenv import load_dotenv

load_dotenv()  # precisa rodar ANTES de importar app, para Config já ler as variáveis do .env

from app import criar_app

app = criar_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
