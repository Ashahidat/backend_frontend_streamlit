import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

# Configuration de la page
st.set_page_config(
    page_title="Tableau de Bord - Analyse des Données",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour récupérer les données depuis Flask (avec cache)
@st.cache_data
def load_data_from_backend(endpoint):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return pd.DataFrame()

# Charger les polices Font Awesome pour les icônes
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """,
    unsafe_allow_html=True
)


st.markdown("<h1 style='text-align: center; color: #2E86C1; font-size: 2.5em; margin-bottom: 30px;'>Tableau de Bord - Analyse des Données</h1>",
        unsafe_allow_html=True)

# Titre principal avec logo
# col1, col2 = st.columns([1, 4])
# with col1:
#     st.image("https://via.placeholder.com/150", width=100)  # Logo (remplacez par votre image)
# with col2:
#     st.markdown(
#         "<h1 style='text-align: center; color: #2E86C1; font-size: 2.5em; margin-bottom: 30px;'>Tableau de Bord - Analyse des Données</h1>",
#         unsafe_allow_html=True
#     )

# Chargement des données (avec cache)
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

# Définir class_names comme la liste de tous les types d'objets
class_names = sorted(set(obj for category in category_mapping.values() for obj in category))

# Sidebar avec les filtres globaux
with st.sidebar:
    st.markdown(
        "<h3 style='color: #2E86C1; font-size: 1.5em; margin-bottom: 10px;'><i class='fas fa-filter'></i> Filtres Globaux</h3>",
        unsafe_allow_html=True
    )
    st.markdown("---")  # Séparateur

    # Filtre des catégories
    if not data_categories.empty:
        categories = data_categories["nom"].unique()
        selected_categories = st.multiselect(
            "Sélectionner une ou plusieurs catégories",
            options=categories,
            default=categories[:1],
            help="Ce filtre s'applique à toutes les sections du tableau de bord."
        )
    
    # Filtre de granularité (global)
    granularite = st.selectbox(
        "Choisissez la granularité de la période :",
        options=["Semaine", "Mois", "Année"],
        key='granularite_global'
    )

    st.markdown(
        "<h3 style='color: #2E86C1; font-size: 1.5em; margin-top: 20px; margin-bottom: 10px;'><i class='fas fa-sliders-h'></i> Filtres Spécifiques</h3>",
        unsafe_allow_html=True
    )
    st.markdown("---")  # Séparateur

    # Filtre spécifique : type d'objet (dynamique en fonction de la catégorie sélectionnée)
    if not data_objets.empty:
        # Récupérer les types d'objets correspondant à la catégorie sélectionnée
        types_objets = []
        for category in selected_categories:
            if category in category_mapping:
                types_objets.extend(category_mapping[category])

        # Si aucune catégorie n'est sélectionnée, afficher tous les types d'objets
        if not selected_categories:
            types_objets = class_names

        # Gestion de la sélection des types d'objets
        if 'previous_categories' not in st.session_state:
            st.session_state.previous_categories = selected_categories
            st.session_state.selected_types = types_objets[:1]  # Valeur par défaut

        # Vérifier si les catégories ont changé
        if st.session_state.previous_categories != selected_categories:
            # Mettre à jour les catégories précédentes
            st.session_state.previous_categories = selected_categories

            # Filtrer les types d'objets sélectionnés pour ne garder que ceux valides
            valid_selected_types = [t for t in st.session_state.selected_types if t in types_objets]

            # Si aucun type d'objet valide n'est sélectionné, réinitialiser à la première valeur
            if not valid_selected_types:
                valid_selected_types = types_objets[:1]

            # Mettre à jour la sélection des types d'objets
            st.session_state.selected_types = valid_selected_types

        # Afficher le filtre spécifique pour les types d'objets
        selected_types = st.multiselect(
            "Types d'objets",
            options=types_objets,
            default=st.session_state.selected_types
        )
        st.markdown("<small>Ne s'appliquent qu'aux premiers graphiques.</small>", unsafe_allow_html=True)

        # Sauvegarder la sélection des types d'objets dans session_state
        st.session_state.selected_types = selected_types

# Section 1 : Nombre d'objets détectés sur une période
st.markdown("---")
st.markdown(
    "<h2 style='color: #2E86C1; font-size: 2em; margin-top: 30px; margin-bottom: 20px;'><i class='fas fa-chart-bar'></i> Nombre d'Objets Détectés</h2>",
    unsafe_allow_html=True
)

if not data_objets.empty:
    # Jointure avec les catégories (avec cache)
    if 'data_objets_merged' not in st.session_state:
        st.session_state.data_objets_merged = data_objets.merge(data_categories, left_on="categorie_id", right_on="id")
    
    # Filtrage des données (global : catégorie)
    filtered_data_objets = st.session_state.data_objets_merged[
        st.session_state.data_objets_merged["nom"].isin(selected_categories)
    ].copy()
    
    # Appliquer le filtre spécifique pour les types d'objets
    if selected_types:
        filtered_data_objets = filtered_data_objets[filtered_data_objets["type_objet"].isin(selected_types)]
    
    # Vérifiez que le DataFrame n'est pas vide après le filtrage
    if filtered_data_objets.empty:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    else:
        # Convertir la date de détection en datetime
        filtered_data_objets['date_detection'] = pd.to_datetime(filtered_data_objets['date_detection'], errors='coerce')

        # Appliquer la granularité globale
        if granularite == "Semaine":
            filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.strftime('%G-W%V')  # ISO week format
        elif granularite == "Mois":
            filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.strftime('%b %Y')  # Ex: 'Sep 2023'
        elif granularite == "Année":
            filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.year.astype(str)  # Format: "2023"

        # Agrégation des données par période et par catégorie
        count_per_period_category = filtered_data_objets.groupby(["periode", "nom"]).size().reset_index(name="Nombre d'objets")

        # Affichage du graphique
        fig = px.bar(
            count_per_period_category,
            x="periode",
            y="Nombre d'objets",
            color="nom",
            labels={"periode": "Période", "Nombre d'objets": "Nombre d'Objets", "nom": "Catégorie"},
            color_discrete_sequence=['#2E86C1', '#28B463', '#E74C3C', '#F39C12']  # Palette de couleurs
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis={'title': 'Période'},
            yaxis={'title': "Nombre d'Objets"},
            barmode="group",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#566573')
        )

        st.plotly_chart(fig, use_container_width=True)


# Section 2 : Vitesse de traitement des objets
st.markdown("---")
st.markdown(
    "<h2 style='color: #2E86C1; font-size: 2em; margin-top: 30px; margin-bottom: 20px;'><i class='fas fa-tachometer-alt'></i> Vitesse de Traitement des Objets</h2>",
    unsafe_allow_html=True
)

if not data_objets.empty:
    # Filtrage des données selon les catégories et la période globale
    filtered_data_objets = st.session_state.data_objets_merged[
        st.session_state.data_objets_merged["nom"].isin(selected_categories)
    ].copy()
    
    # Appliquer le filtre spécifique pour les types d'objets
    if selected_types:
        filtered_data_objets = filtered_data_objets[filtered_data_objets["type_objet"].isin(selected_types)]
    
    # Vérifiez que le DataFrame n'est pas vide après le filtrage
    if filtered_data_objets.empty:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    else:
        # Convertir la date de détection en datetime
        filtered_data_objets['date_detection'] = pd.to_datetime(filtered_data_objets['date_detection'], errors='coerce')

        # Appliquer la granularité globale
        if granularite == "Semaine":
            filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.strftime('%G-W%V')
        elif granularite == "Mois":
            filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.strftime('%b %Y')
        elif granularite == "Année":
            filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.year.astype(str)

        # Agrégation des données par période et par catégorie
        count_per_period_category = filtered_data_objets.groupby(["periode", "nom"]).size().reset_index(name="Nombre d'objets")

        # Calcul de la vitesse de traitement
        count_per_period_category['Vitesse de traitement (objets/min)'] = count_per_period_category.groupby("periode")["Nombre d'objets"].transform(lambda x: x / 60)

        # Affichage du graphique
        fig = px.bar(
            count_per_period_category,
            x="periode",
            y="Vitesse de traitement (objets/min)",
            color="nom",
            labels={"periode": "Période", "Vitesse de traitement (objets/min)": "Vitesse de traitement (objets/min)", "nom": "Catégorie"},
            color_discrete_sequence=['#2E86C1', '#28B463', '#E74C3C', '#F39C12']
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis={'title': 'Période'},
            yaxis={'title': "Vitesse de traitement (objets/min)"},
            barmode="group",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#566573')
        )

        st.plotly_chart(fig, use_container_width=True)

# Section 3 : Tendance des Objets Détectés
st.markdown("---")
st.markdown(
    "<h2 style='color: #2E86C1; font-size: 2em; margin-top: 30px; margin-bottom: 20px;'><i class='fas fa-chart-line'></i> Tendance des Objets Détectés</h2>",
    unsafe_allow_html=True
)

if not data_objets.empty:
    # Filtrage des données selon les catégories sélectionnées
    filtered_data_objets = st.session_state.data_objets_merged[
        st.session_state.data_objets_merged["nom"].isin(selected_categories)
    ].copy()

    # Convertir la date de détection en datetime
    filtered_data_objets['date_detection'] = pd.to_datetime(filtered_data_objets['date_detection'], errors='coerce')

    # Appliquer la granularité globale sur les périodes
    if granularite == "Semaine":
        filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.strftime('%Y-W%V')  # Format YYYY-WEEK
    elif granularite == "Mois":
        filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.strftime('%Y-%m')  # Format YYYY-MM
    elif granularite == "Année":
        filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.strftime('%Y')  # Format YYYY

    # Agrégation des données par période et catégorie
    count_per_period_category = filtered_data_objets.groupby(["periode", "nom"]).size().reset_index(name="Nombre d'objets")

    # Vérifier s'il y a des données après l'agrégation
    if count_per_period_category.empty:
        st.warning("Aucune donnée disponible pour la tendance des objets détectés.")
    else:
        # Forcer le tri des périodes pour éviter un affichage désordonné
        count_per_period_category = count_per_period_category.sort_values("periode")

       # Création des sous-graphiques
fig_trend = sp.make_subplots(
    rows=len(selected_categories), 
    cols=1, 
    shared_xaxes=True,  # Partager l'axe X pour toutes les catégories
    vertical_spacing=0.1,  # Espacement entre les subplots
    subplot_titles=[f"Tendance pour {cat}" for cat in selected_categories]  # Titres des sous-graphiques
)

# Ajouter une ligne de tendance pour chaque catégorie
for idx, category in enumerate(selected_categories):
    category_data = count_per_period_category[count_per_period_category['nom'] == category]

    # Lissage des tendances avec une moyenne glissante
    trend_line = category_data["Nombre d'objets"].rolling(window=2, min_periods=1).mean()

    fig_trend.add_trace(
        go.Scatter(
            x=category_data['periode'],
            y=trend_line,
            mode='lines+markers',
            name=category,
            line=dict(color='#2E86C1', width=2),  # Couleur de la ligne
            marker=dict(color='#F39C12', size=8),  # Couleur des marqueurs
        ),
        row=idx + 1, col=1
    )

# Mise en forme du graphique
fig_trend.update_layout(
    height=250 * len(selected_categories),  # Ajustement dynamique de la hauteur
    template="plotly_white",
    showlegend=False,  # Désactiver la légende (les titres des sous-graphiques suffisent)
    plot_bgcolor='white',  # Fond blanc
    paper_bgcolor='white',  # Fond blanc
    font=dict(color='#566573'),  # Couleur du texte
)

# Forcer l'axe X en tant que catégorie et ajouter un ordre
fig_trend.update_xaxes(
    title_text="Période", 
    row=len(selected_categories), col=1,
    type='category',  # Spécifier que l'axe est catégoriel
    categoryorder='category ascending'  # Assurer que les périodes sont triées correctement
)

# Afficher le graphique
st.plotly_chart(fig_trend, use_container_width=True)


# Section 4 : Taux de précision
st.markdown("---")
st.markdown(
    "<h2 style='color: #2E86C1; font-size: 2em; margin-top: 30px; margin-bottom: 20px;'><i class='fas fa-percentage'></i> Taux de Précision</h2>",
    unsafe_allow_html=True
)

if not data_satisfaction.empty:
    # Filtrer les données en fonction des catégories sélectionnées
    if 'categorie' in data_satisfaction.columns:
        if selected_categories:
            filtered_data = data_satisfaction[data_satisfaction["categorie"].isin(selected_categories)].copy()
        else:
            filtered_data = data_satisfaction.copy()
    else:
        st.warning("La colonne 'categorie' est manquante dans les données.")
        filtered_data = data_satisfaction

    # Vérifiez que le DataFrame n'est pas vide après le filtrage
    if filtered_data.empty:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    else:
        # Convertir la date de détection en datetime
        filtered_data['date_detection'] = pd.to_datetime(filtered_data['date_detection'], errors='coerce')

        # Appliquer la granularité globale
        if granularite == "Semaine":
            filtered_data['periode'] = filtered_data['date_detection'].dt.strftime('%G-W%V')
        elif granularite == "Mois":
            filtered_data['periode'] = filtered_data['date_detection'].dt.strftime('%Y-%m')
        elif granularite == "Année":
            filtered_data['periode'] = filtered_data['date_detection'].dt.strftime('%Y')

        # Agrégation des données par période et par catégorie
        count_per_period_category = filtered_data.groupby(["periode", "categorie"]).agg({
            "satisfait": "sum",
            "non_satisfait": "sum"
        }).reset_index()

        # Calculer le taux de précision
        count_per_period_category["taux_precision"] = (
            count_per_period_category["satisfait"] / 
            (count_per_period_category["satisfait"] + count_per_period_category["non_satisfait"])
        ) * 100

        # Créer le graphique en barres
        fig_satisfaction = px.bar(
            count_per_period_category,
            x="periode",
            y="taux_precision",
            color="categorie",
            labels={"taux_precision": "Taux de Précision (%)", "periode": "Période"},
            color_discrete_sequence=['#2E86C1', '#28B463', '#E74C3C', '#F39C12']  # Palette de couleurs
        )

        # Forcer l'axe X à être catégorique
        fig_satisfaction.update_layout(xaxis_type='category')

        # Afficher le graphique
        st.plotly_chart(fig_satisfaction, use_container_width=True)

