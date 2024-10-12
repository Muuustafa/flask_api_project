from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Post, User
from .schemas import post_schema, posts_schema
from .schemas import user_schema, users_schema
from .auth import generate_token, token_required
from . import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/')
def home():
    return jsonify({'message': 'Bienvenue dans l\'API Flask !'}), 200

@api_bp.route('/users', methods=['POST'])
def create_user():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    role = request.json.get('role')

    # Vérifier que tous les champs sont fournis
    if not username or not email or not password:
        return jsonify({'message': 'Tous les champs sont obligatoires'}), 400

    # Hachage du mot de passe
    password_hash = generate_password_hash(password)

    # Créer un nouvel utilisateur
    new_user = User(username=username, email=email, password=password_hash, role=role)
    db.session.add(new_user)
    db.session.commit()

    # Sérialiser les données de l'utilisateur et les renvoyer
    user_data = user_schema.dump(new_user)
    return jsonify(user_data), 201

@api_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    # Sérialiser la liste d'utilisateurs
    users_data = users_schema.dump(users)
    return jsonify(users_data), 200

@api_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    # Sérialiser les données de l'utilisateur
    user_data = user_schema.dump(user)
    return jsonify(user_data), 200

@api_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    user.username = request.json.get('username', user.username)
    user.email = request.json.get('email', user.email)
    user.role = request.json.get('role', user.role)
    db.session.commit()

    # Sérialiser les données mises à jour de l'utilisateur
    user_data = user_schema.dump(user)
    return jsonify(user_data), 200

@api_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Utilisateur supprimé avec succès'}), 204

@api_bp.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    # Vérifier que l'email et le mot de passe sont fournis
    if not email or not password:
        return jsonify({'message': 'Email et mot de passe sont obligatoires'}), 400

    # Rechercher l'utilisateur dans la base de données
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Identifiants incorrects'}), 401

    # Générer un token JWT
    token = generate_token(user.id)

    return jsonify({'token': token}), 200


# Route pour créer un article (Post)
@api_bp.route('/posts', methods=['POST'])
def create_post():
    title = request.json.get('title')
    body = request.json.get('body')
    user_id = request.json.get('user_id')

    # Vérifier que les champs requis sont fournis
    if not title or not body or not user_id:
        return jsonify({'message': 'Les champs title, body et user_id sont obligatoires'}), 400

    # Vérifier si l'utilisateur existe
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404

    # Créer un nouvel article
    new_post = Post(title=title, body=body, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()

    # Retourner l'article créé
    post_data = post_schema.dump(new_post)
    return jsonify(post_data), 201

# Route pour obtenir tous les articles
@api_bp.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    # Sérialiser la liste des articles
    posts_data = posts_schema.dump(posts)
    return jsonify(posts_data), 200

# Route pour obtenir un article spécifique par ID
@api_bp.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get_or_404(id)
    # Sérialiser les données de l'article
    post_data = post_schema.dump(post)
    return jsonify(post_data), 200

# Route pour mettre à jour un article
@api_bp.route('/posts/<int:id>', methods=['PUT'])
def update_post(id):
    post = Post.query.get_or_404(id)
    post.title = request.json.get('title', post.title)
    post.body = request.json.get('body', post.body)
    db.session.commit()

    # Sérialiser les données mises à jour de l'article
    post_data = post_schema.dump(post)
    return jsonify(post_data), 200

# Route pour supprimer un article
@api_bp.route('/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()

    return jsonify({'message': 'Article supprimé avec succès'}), 204

@api_bp.route('/protected', methods=['GET'])
@token_required
def protected_route(user_id):
    return jsonify({'message': f'Accès autorisé pour l\'utilisateur {user_id}'})
