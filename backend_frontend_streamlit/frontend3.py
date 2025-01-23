import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Tableau de Bord - Analyse des Données", layout="wide")

# Fonction pour récupérer les données depuis Flask
def load_data_from_backend(endpoint):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return pd.DataFrame()

# Titre principal
st.markdown("<h1 style='text-align: center; color: #2E86C1;'>Tableau de Bord - Analyse des Données</h1>", unsafe_allow_html=True)

# Chargement des données
data_objets = load_data_from_backend("http://localhost:5000/data/objets")
data_satisfaction = load_data_from_backend("http://localhost:5000/data/satisfaction")
data_categories = load_data_from_backend("http://localhost:5000/data/categories")

# Mapping des types d'objets aux catégories
category_mapping = {
    "Transport": ["bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat"],
    "Signalisation et Infrastructure": ["traffic light", "fire hydrant", "stop sign", "parking meter", "bench"],
    "Animaux": ["bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"],
    "Accessoires personnels": ["backpack", "umbrella", "handbag", "tie", "suitcase"],
    "Sports et Loisirs": ["frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket"],
    "Cuisine et Nourriture": ["bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake"],
    "Mobilier": ["chair", "sofa", "pottedplant", "bed", "diningtable", "toilet"],
    "Électronique": ["tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator"],
    "Lecture et Décoration": ["book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]
}

# Filtres globaux (placés dans la barre latérale)
with st.sidebar:
    st.markdown("<h3 style='color: #2E86C1;'>Filtres Globaux</h3>", unsafe_allow_html=True)
    
    # Filtre des catégories
    if not data_categories.empty:
        categories = data_categories["nom"].unique()
        selected_categories = st.multiselect(
            "Sélectionner une ou plusieurs catégories",
            options=categories,
            default=categories[:1],
            help="Ce filtre s'applique à toutes les sections du tableau de bord."
        )

# Section 1 : Nombre d'objets détectés sur une période
st.markdown("<h2 style='color: #2E86C1;'>Nombre d'Objets Détectés</h2>", unsafe_allow_html=True)
if not data_objets.empty:
    # Jointure avec les catégories
    data_objets = data_objets.merge(data_categories, left_on="categorie_id", right_on="id")
    
    # Filtrage des données (global : catégorie)
    filtered_data_objets = data_objets[data_objets["nom"].isin(selected_categories)].copy()
    
    # Créer deux colonnes : une pour les filtres, une pour le graphique
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Filtre spécifique : type d'objet (dynamique en fonction de la catégorie sélectionnée)
        if not filtered_data_objets.empty:
            # Récupérer les types d'objets correspondant à la catégorie sélectionnée
            types_objets = []
            for category in selected_categories:
                if category in category_mapping:
                    types_objets.extend(category_mapping[category])
            
            # Si aucune catégorie n'est sélectionnée, afficher tous les types d'objets
            if not selected_categories:
                types_objets = class_names
            
            # Afficher le filtre spécifique
            selected_types = st.multiselect(
                "Sélectionner un ou plusieurs types d'objets (spécifique à cette section)",
                options=types_objets,
                default=types_objets[:1] if types_objets else [],
                help="Ce filtre s'applique uniquement à cette section."
            )
            
            # Appliquer le filtre spécifique
            if selected_types:
                filtered_data_objets = filtered_data_objets[filtered_data_objets["type_objet"].isin(selected_types)]
        
        # Visualisation des filtres actifs
        st.markdown(f"**Filtres actifs :** Catégorie = {', '.join(selected_categories)}, Type d'objet = {', '.join(selected_types)}")
    
    with col2:
        # Vérifiez que le DataFrame n'est pas vide après le filtrage
        if filtered_data_objets.empty:
            st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
        else:
            # Traitement des données
            filtered_data_objets['date_detection'] = pd.to_datetime(filtered_data_objets['date_detection'], errors='coerce')
            
            granularite = st.selectbox(
                "Choisissez la granularité de la période :",
                options=["Semaine", "Mois", "Année"],
                key='granularite'
            )
            
            if granularite == "Semaine":
                filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.to_period('W').astype(str)
            elif granularite == "Mois":
                filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.to_period('M').astype(str)
            elif granularite == "Année":
                filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.to_period('Y').astype(str)

            count_per_period = filtered_data_objets.groupby("periode").size().reset_index(name="Nombre d'objets")

            # Affichage du graphique
            fig = px.line(
                count_per_period,
                x="periode",
                y="Nombre d'objets",
                labels={"periode": "Période", "Nombre d'objets": "Nombre d'Objets"},
                title=f"Nombre d'Objets Détectés par {granularite}",
                color_discrete_sequence=[px.colors.qualitative.Plotly[0]]
            )
            st.plotly_chart(fig, use_container_width=True)

# Section 2 : Degré de satisfaction des utilisateurs
st.markdown("<h2 style='color: #2E86C1;'>Degré de Satisfaction des Utilisateurs</h2>", unsafe_allow_html=True)
if not data_satisfaction.empty:
    # Vérifiez que la colonne 'genre' existe
    if 'genre' not in data_satisfaction.columns:
        st.error("La colonne 'genre' est manquante dans les données de satisfaction.")
    else:
        # Dictionnaire de correspondance entre les libellés et les valeurs de la base de données
        genre_mapping = {
            "Tous": "Tous",
            "Femme": "F",
            "Homme": "H"
        }
        
        # Créer deux colonnes : une pour les filtres, une pour le graphique
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Filtre spécifique : genre (choix unique)
            selected_genre_label = st.radio(
                "Sélectionner un genre (spécifique à cette section)",
                options=["Tous", "Femme", "Homme"],  # Libellés intuitifs
                index=0,  # Par défaut, "Tous" est sélectionné
                key='satisfaction_genre',
                help="Ce filtre s'applique uniquement à cette section."
            )
            
            # Récupérer la valeur correspondante dans la base de données
            selected_genre_value = genre_mapping[selected_genre_label]
            
            # Filtrage des données (spécifique : genre)
            if selected_genre_value == "Tous":
                filtered_data_satisfaction = data_satisfaction.copy()
            else:
                filtered_data_satisfaction = data_satisfaction[data_satisfaction["genre"] == selected_genre_value].copy()
            
            # Visualisation des filtres actifs
            st.markdown(f"**Filtre actif :** Genre = {selected_genre_label}")
        
        with col2:
            # Vérifiez que les données filtrées ne sont pas vides
            if filtered_data_satisfaction.empty:
                st.warning(f"Aucune donnée trouvée pour le genre sélectionné : {selected_genre_label}.")
            else:
                # Répartition de la satisfaction
                total_satisfait = filtered_data_satisfaction['satisfait'].sum()
                total_non_satisfait = filtered_data_satisfaction['non_satisfait'].sum()

                satisfaction_data = pd.DataFrame({
                    "Catégorie": ["Satisfaits", "Non satisfaits"],
                    "Valeurs": [total_satisfait, total_non_satisfait]
                })

                fig = px.pie(
                    satisfaction_data,
                    values="Valeurs",
                    names="Catégorie",
                    hole=0.4,
                    title="Répartition de la Satisfaction des Utilisateurs",
                    color_discrete_sequence=[px.colors.qualitative.Plotly[1], px.colors.qualitative.Plotly[2]]
                )
                st.plotly_chart(fig, use_container_width=True)

# Section 3 : Vitesse de traitement et temps moyen par détection
st.markdown("<h2 style='color: #2E86C1;'>Vitesse de Traitement</h2>", unsafe_allow_html=True)
if not data_objets.empty:
    # Filtrage des données (global : catégorie)
    filtered_data_objets = data_objets[data_objets["nom"].isin(selected_categories)].copy()
    
    # Créer deux colonnes : une pour les filtres, une pour le graphique
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Filtre spécifique : type d'objet
        if not filtered_data_objets.empty:
            types_objets = filtered_data_objets["type_objet"].unique()
            selected_types = st.multiselect(
                "Sélectionner un ou plusieurs types d'objets (spécifique à cette section)",
                options=types_objets,
                default=types_objets[:1],
                key='vitesse_filter',
                help="Ce filtre s'applique uniquement à cette section."
            )
            filtered_data_objets = filtered_data_objets[filtered_data_objets["type_objet"].isin(selected_types)]
        
        # Visualisation des filtres actifs
        st.markdown(f"**Filtres actifs :** Catégorie = {', '.join(selected_categories)}, Type d'objet = {', '.join(selected_types)}")
    
    with col2:
        # Vérifiez que le DataFrame n'est pas vide après le filtrage
        if filtered_data_objets.empty:
            st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
        else:
            # Vérifiez que 'date_detection' existe et est correctement formatée
            if 'date_detection' not in filtered_data_objets.columns:
                st.error("La colonne 'date_detection' est manquante dans les données filtrées.")
            else:
                # Convertir 'date_detection' en datetime
                filtered_data_objets['date_detection'] = pd.to_datetime(filtered_data_objets['date_detection'], errors='coerce')
                
                # Vérifiez que la conversion a réussi
                if filtered_data_objets['date_detection'].isnull().all():
                    st.error("La colonne 'date_detection' n'a pas pu être convertie en datetime.")
                else:
                    # Créer la colonne 'periode'
                    if granularite == "Semaine":
                        filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.to_period('W').astype(str)
                    elif granularite == "Mois":
                        filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.to_period('M').astype(str)
                    elif granularite == "Année":
                        filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.to_period('Y').astype(str)
                    
                    # Calcul du temps moyen de réponse par période
                    response_time_per_period = filtered_data_objets.groupby("periode")['temps_reponse'].mean().reset_index(name="Temps Moyen de Réponse (heures)")
                    
                    # Affichage du graphique
                    fig = px.line(
                        response_time_per_period,
                        x="periode",
                        y="Temps Moyen de Réponse (heures)",
                        labels={"periode": "Période", "Temps Moyen de Réponse (heures)": "Temps Moyen de Réponse (heures)"},
                        title=f"Temps Moyen de Réponse par {granularite}",
                        color_discrete_sequence=[px.colors.qualitative.Plotly[3]]
                    )
                    st.plotly_chart(fig, use_container_width=True)