from dotenv import load_dotenv

load_dotenv()  # precisa rodar ANTES de importar app, para Config já ler as variáveis do .env

from app import criar_app

app = criar_app()

import os

from flask_cors import CORS
CORS(app)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_ENV") == "development"
    )
