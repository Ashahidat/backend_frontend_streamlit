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

# Filtres globaux (placés dans la barre latérale)
with st.sidebar:
    st.markdown("<h3 style='color: #2E86C1;'>Filtres Globaux</h3>", unsafe_allow_html=True)
    
    # Filtre de granularité (commun à plusieurs graphiques)
    granularite = st.selectbox(
        "Choisissez la granularité de la période :",
        options=["Semaine", "Mois", "Année"],
        key='granularite'
    )
    
    # Filtre des types d'objets (pour les graphiques liés aux objets)
    if not data_objets.empty:
        objets_types = data_objets["type_objet"].unique()
        selected_objets = st.multiselect(
            "Sélectionner un ou plusieurs types d'objets",
            options=objets_types,
            default=objets_types[:1]
        )

# Palette de couleurs adaptée pour un fond clair
colors = px.colors.qualitative.Plotly  # Palette moderne et harmonieuse

# Section 1 : Nombre d'objets détectés sur une période
st.markdown("<h2 style='color: #2E86C1;'>Nombre d'Objets Détectés</h2>", unsafe_allow_html=True)
if not data_objets.empty:
    # Traitement des données
    data_objets['date_detection'] = pd.to_datetime(data_objets['date_detection'], errors='coerce')
    filtered_data_objets = data_objets[data_objets["type_objet"].isin(selected_objets)].copy()  # Copie explicite

    if granularite == "Semaine":
        filtered_data_objets.loc[:, 'periode'] = filtered_data_objets['date_detection'].dt.to_period('W').astype(str)
    elif granularite == "Mois":
        filtered_data_objets.loc[:, 'periode'] = filtered_data_objets['date_detection'].dt.to_period('M').astype(str)
    elif granularite == "Année":
        filtered_data_objets.loc[:, 'periode'] = filtered_data_objets['date_detection'].dt.to_period('Y').astype(str)

    count_per_period = filtered_data_objets.groupby("periode").size().reset_index(name="Nombre d'objets")

    # Affichage du graphique
    fig = px.line(
        count_per_period,
        x="periode",
        y="Nombre d'objets",
        labels={"periode": "Période", "Nombre d'objets": "Nombre d'Objets"},
        title=f"Nombre d'Objets Détectés par {granularite}",
        color_discrete_sequence=[colors[0]]  # Utilisation de la première couleur de la palette
    )
    fig.update_layout(
        plot_bgcolor='rgba(255, 255, 255, 1)',  # Fond blanc
        paper_bgcolor='rgba(255, 255, 255, 1)',  # Fond blanc
        font=dict(color='black')  # Texte en noir
    )
    st.plotly_chart(fig, use_container_width=True)

# Section 2 : Degré de satisfaction des utilisateurs
st.markdown("<h2 style='color: #2E86C1;'>Degré de Satisfaction des Utilisateurs</h2>", unsafe_allow_html=True)
if not data_satisfaction.empty:
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("<h4 style='color: #2E86C1;'>Filtres</h4>", unsafe_allow_html=True)
        # Filtre spécifique à la satisfaction
        satisfaction_filter = st.selectbox(
            "Filtrer par type de réponse :",
            options=["Toutes", "Satisfaits", "Non satisfaits"],
            key='satisfaction_filter'
        )
    
    with col2:
        # Répartition de la satisfaction
        if satisfaction_filter == "Toutes":
            total_satisfait = data_satisfaction['satisfait'].sum()
            total_non_satisfait = data_satisfaction['non_satisfait'].sum()
        elif satisfaction_filter == "Satisfaits":
            total_satisfait = data_satisfaction['satisfait'].sum()
            total_non_satisfait = 0
        elif satisfaction_filter == "Non satisfaits":
            total_satisfait = 0
            total_non_satisfait = data_satisfaction['non_satisfait'].sum()

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
            color_discrete_sequence=[colors[1], colors[2]]  # Utilisation de deux couleurs de la palette
        )
        fig.update_layout(
            plot_bgcolor='rgba(255, 255, 255, 1)',  # Fond blanc
            paper_bgcolor='rgba(255, 255, 255, 1)',  # Fond blanc
            font=dict(color='black')  # Texte en noir
        )
        st.plotly_chart(fig, use_container_width=True)

# Section 3 : Vitesse de traitement et temps moyen par détection
st.markdown("<h2 style='color: #2E86C1;'>Vitesse de Traitement</h2>", unsafe_allow_html=True)
if not data_objets.empty:
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("<h4 style='color: #2E86C1;'>Filtres</h4>", unsafe_allow_html=True)
        # Filtre spécifique à la vitesse de traitement
        vitesse_filter = st.selectbox(
            "Filtrer par type d'objet :",
            options=["Tous"] + list(data_objets["type_objet"].unique()),
            key='vitesse_filter'
        )
    
    with col2:
        # Traitement des données
        data_objets['date_detection'] = pd.to_datetime(data_objets['date_detection'], errors='coerce')

        if vitesse_filter != "Tous":
            filtered_data_objets = data_objets[data_objets["type_objet"] == vitesse_filter].copy()  # Copie explicite
        else:
            filtered_data_objets = data_objets.copy()  # Copie explicite

        if granularite == "Semaine":
            filtered_data_objets.loc[:, 'periode'] = filtered_data_objets['date_detection'].dt.to_period('W').astype(str)
        elif granularite == "Mois":
            filtered_data_objets.loc[:, 'periode'] = filtered_data_objets['date_detection'].dt.to_period('M').astype(str)
        elif granularite == "Année":
            filtered_data_objets.loc[:, 'periode'] = filtered_data_objets['date_detection'].dt.to_period('Y').astype(str)

        # Calcul du temps moyen de réponse par période
        response_time_per_period = filtered_data_objets.groupby("periode")['temps_reponse'].mean().reset_index(name="Temps Moyen de Réponse (heures)")

        # Affichage du graphique
        fig = px.line(
            response_time_per_period,
            x="periode",
            y="Temps Moyen de Réponse (heures)",
            labels={"periode": "Période", "Temps Moyen de Réponse (heures)": "Temps Moyen de Réponse (heures)"},
            title=f"Temps Moyen de Réponse par {granularite}",
            color_discrete_sequence=[colors[3]]  # Utilisation d'une autre couleur de la palette
        )
        fig.update_layout(
            plot_bgcolor='rgba(255, 255, 255, 1)',  # Fond blanc
            paper_bgcolor='rgba(255, 255, 255, 1)',  # Fond blanc
            font=dict(color='black')  # Texte en noir
        )
        st.plotly_chart(fig, use_container_width=True)

# Section 4 : Répartition des types d'objets détectés
st.markdown("<h2 style='color: #2E86C1;'>Répartition des Types d'Objets Détectés</h2>", unsafe_allow_html=True)
if not data_objets.empty:
    # Répartition des types d'objets
    type_counts = data_objets['type_objet'].value_counts().reset_index()
    type_counts.columns = ['Type d\'objet', 'Nombre d\'objets']
    
    fig = px.bar(
        type_counts,
        x='Type d\'objet',
        y='Nombre d\'objets',
        labels={'Type d\'objet': 'Type d\'objet', 'Nombre d\'objets': 'Nombre d\'objets'},
        title="Répartition des Types d'Objets Détectés",
        color_discrete_sequence=[colors[4]]  # Utilisation d'une autre couleur de la palette
    )
    fig.update_layout(
        plot_bgcolor='rgba(255, 255, 255, 1)',  # Fond blanc
        paper_bgcolor='rgba(255, 255, 255, 1)',  # Fond blanc
        font=dict(color='black')  # Texte en noir
    )
    st.plotly_chart(fig, use_container_width=True)

# Section 5 : Temps de réponse par type d'objet
st.markdown("<h2 style='color: #2E86C1;'>Temps de Réponse par Type d'Objet</h2>", unsafe_allow_html=True)
if not data_objets.empty:
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("<h4 style='color: #2E86C1;'>Filtres</h4>", unsafe_allow_html=True)
        # Filtre spécifique au temps de réponse par type d'objet
        response_filter = st.selectbox(
            "Filtrer par type d'objet :",
            options=["Tous"] + list(data_objets["type_objet"].unique()),
            key='response_filter'
        )
    
    with col2:
        # Temps de réponse par type d'objet
        if response_filter != "Tous":
            filtered_data_objets = data_objets[data_objets["type_objet"] == response_filter].copy()  # Copie explicite
        else:
            filtered_data_objets = data_objets.copy()  # Copie explicite

        response_time_by_type = filtered_data_objets.groupby('type_objet')['temps_reponse'].mean().reset_index(name="Temps Moyen de Réponse (heures)")
        
        fig = px.bar(
            response_time_by_type,
            x='type_objet',
            y='Temps Moyen de Réponse (heures)',
            labels={'type_objet': 'Type d\'objet', 'Temps Moyen de Réponse (heures)': 'Temps Moyen de Réponse (heures)'},
            title="Temps de Réponse Moyen par Type d'Objet",
            color_discrete_sequence=[colors[5]]  # Utilisation d'une autre couleur de la palette
        )
        fig.update_layout(
            plot_bgcolor='rgba(255, 255, 255, 1)',  # Fond blanc
            paper_bgcolor='rgba(255, 255, 255, 1)',  # Fond blanc
            font=dict(color='black')  # Texte en noir
        )
        st.plotly_chart(fig, use_container_width=True)