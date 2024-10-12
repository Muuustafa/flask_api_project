# tests/conftest.py
import pytest
from app import create_app, db
import os
import sys

# Ajouter le chemin du dossier de base du projet dans PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql:///:memory:",
        "SECRET_KEY": "testsecretkey",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
