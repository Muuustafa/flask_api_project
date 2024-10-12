# Utiliser l'image Python officielle version 3.9 slim
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers de l'application dans le conteneur
COPY . .

RUN flask db upgrade

# Exposer le port sur lequel Flask écoute
EXPOSE 5000

# Définir la variable d'environnement FLASK_APP
ENV FLASK_APP=run.py

# Définir la commande par défaut pour exécuter l'application
CMD ["flask", "run", "--host=0.0.0.0"]
