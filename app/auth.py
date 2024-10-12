import jwt
from flask import request, jsonify, current_app
from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import User, db

auth_bp = Blueprint('auth', __name__)

# Route d'inscription (registre)
@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Tous les champs sont obligatoires"}), 400

    # Hashage du mot de passe
    password_hash = generate_password_hash(password)

    # Créer un nouvel utilisateur
    new_user = User(username=username, email=email, password=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Utilisateur créé avec succès"}), 201

# Route de login
@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    # Rechercher l'utilisateur
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Identifiants incorrects"}), 401

    # Générer un token JWT
    token = create_access_token(identity=user.id)

    return jsonify({"token": token}), 200


# Fonction pour vérifier si l'utilisateur est admin
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != 'admin':
            return jsonify({"msg": "Accès interdit"}), 403
        return fn(*args, **kwargs)
    return wrapper


# Route protégée par un rôle admin
@auth_bp.route('/admin_only', methods=['GET'])
@jwt_required()
@admin_required  # Seuls les admins peuvent accéder
def admin_only_route():
    return jsonify({"msg": "Bienvenue, admin!"}), 200



# Fonction pour générer un token JWT
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=30)  # Durée de validité du token
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")
    return token

# Décorateur pour sécuriser les routes avec JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token manquant!'}), 403

        try:
            # Décoder le token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # Extraire l'ID de l'utilisateur à partir du payload
            user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expiré!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalide!'}), 403

        # Passer l'utilisateur dans les arguments de la fonction décorée
        return f(user_id=user_id, *args, **kwargs)
    return decorated


# Route protégée par un rôle admin
@auth_bp.route('/admin_only', methods=['GET'])
@jwt_required()
@admin_required  # Seuls les admins peuvent accéder
def admin_only_route():
    return jsonify({"msg": "Bienvenue, admin!"}), 200