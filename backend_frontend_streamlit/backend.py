import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

# Connexion à la base de données MySQL avec pymysql
def get_db_connection():
    return pymysql.connect(
        host="localhost",  # Remplace par ton hôte
        user="root",       # Remplace par ton utilisateur MySQL
        password="",       # Remplace par ton mot de passe
        database="prediction",  # Nom de la base de données
        cursorclass=pymysql.cursors.DictCursor
    )

# Route pour obtenir des données des objets
@app.route('/data/objets', methods=['GET'])
def get_objets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM objets")
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

# Route pour obtenir des données de satisfaction
@app.route('/data/satisfaction', methods=['GET'])
def get_satisfaction():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Jointure avec la table utilisateurs pour récupérer le genre
    cursor.execute("""
    SELECT s.*, c.nom AS categorie, o.date_detection
    FROM satisfactions s
    JOIN objets o ON s.utilisateur_id = o.utilisateur_id
    JOIN categories c ON o.categorie_id = c.id;
    """)
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

# Route pour obtenir des données des catégories
@app.route('/data/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)