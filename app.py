import os
from datetime import timedelta
from flask import Flask
from database import init_db
from routes import main_bp

app = Flask(__name__)
app.secret_key = 'pigeonsocial_secret_key_change_this'
app.permanent_session_lifetime = timedelta(days=31)

# Inicializar base de dados automaticamente ao arrancar
with app.app_context():
    init_db()

# Registar a Blueprint principal que contém todas as rotas em routes.py
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
