import random
import string
import pymysql
from faker import Faker

# Configuration de connexion à MySQL
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "prediction"
}

# Initialiser Faker pour générer des données réalistes
faker = Faker()
faker.unique.clear()  # Réinitialiser le tracker d'unicité au cas où

# Générer des catégories fixes
categories = [
    "Transport", "Signalisation et Infrastructure", "Animaux", 
    "Accessoires personnels", "Sports et Loisirs", 
    "Cuisine et Nourriture", "Mobilier", "Électronique", "Lecture et Décoration"
]

# Générer des types d'objets
class_names = [
    "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", 
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", 
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", 
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", 
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", 
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", 
    "chair", "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor", "laptop", 
    "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", 
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]

# Fonction pour insérer des données
def insert_data():
    try:
        # Connexion à la base de données avec pymysql
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # Optionnel : Réinitialiser les tables
        print("Réinitialisation des tables...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")  # Désactiver les contraintes pour TRUNCATE
        cursor.execute("TRUNCATE TABLE categories;")
        cursor.execute("TRUNCATE TABLE utilisateurs;")
        cursor.execute("TRUNCATE TABLE objets;")
        cursor.execute("TRUNCATE TABLE satisfaction;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # Réactiver les contraintes

        # Insérer les catégories
        print("Insertion des catégories...")
        cursor.executemany(
            "INSERT INTO categories (id, nom) VALUES (%s, %s)",
            [(i + 1, categories[i]) for i in range(len(categories))]
        )

        # Générer et insérer des utilisateurs
        print("Insertion des utilisateurs...")
        utilisateurs = [
            (
                i + 1,
                faker.unique.email(),  # Générer des emails uniques
                "".join(random.choices(string.ascii_letters + string.digits, k=10)),  # mot de passe aléatoire
                random.randint(0, 100),  # nb_predictions
                random.choice(["H", "F"])  # genre
            )
            for i in range(1000)
        ]
        cursor.executemany(
            "INSERT INTO utilisateurs (id, email, mot_de_passe, nb_predictions, genre) VALUES (%s, %s, %s, %s, %s)",
            utilisateurs
        )

        # Générer et insérer des objets
        print("Insertion des objets...")
        objets = [
            (
                i + 1,
                random.randint(1, 1000),  # utilisateur_id
                random.choice(class_names),  # type_objet
                faker.image_url(),  # image_url
                round(random.uniform(0.5, 60.0), 2),  # temps_reponse
                faker.date_between(start_date="-2y", end_date="today"),  # date_detection
                random.randint(1, len(categories))  # categorie_id
            )
            for i in range(1000)
        ]
        cursor.executemany(
            "INSERT INTO objets (id, utilisateur_id, type_objet, image_url, temps_reponse, date_detection, categorie_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            objets
        )

        # Générer et insérer des enregistrements de satisfaction
        print("Insertion des données de satisfaction...")
        satisfaction = [
            (
                i + 1,
                random.randint(1, 1000),  # utilisateur_id
                random.randint(0, 1),  # satisfait
                random.randint(0, 1)  # non_satisfait
            )
            for i in range(1000)
        ]
        cursor.executemany(
            "INSERT INTO satisfaction (id, utilisateur_id, satisfait, non_satisfait) VALUES (%s, %s, %s, %s)",
            satisfaction
        )

        # Valider les changements
        conn.commit()
        print("Données insérées avec succès !")

    except pymysql.MySQLError as err:
        print(f"Erreur : {err}")
    finally:
        # Fermer la connexion si elle est ouverte
        if conn:
            cursor.close()
            conn.close()

# Exécuter l'insertion
insert_data()
