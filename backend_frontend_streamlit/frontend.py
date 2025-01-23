# import streamlit as st
# import requests
# import pandas as pd
# import plotly.express as px
# import datetime

# # Configuration de la page
# st.set_page_config(page_title="Visualisation des Données", layout="wide")

# # Fonction pour récupérer les données depuis Flask
# def load_data_from_backend(endpoint):
#     try:
#         response = requests.get(endpoint)
#         response.raise_for_status()
#         return pd.DataFrame(response.json())
#     except requests.RequestException as e:
#         st.error(f"Erreur lors de la récupération des données : {e}")
#         return pd.DataFrame()

# # Titre centré en HTML
# st.markdown("<h1 style='text-align: center;'>Analyse des Données</h1>", unsafe_allow_html=True)


# # Fonction pour afficher les filtres et les graphiques des objets
# def afficher_objets():
#     data_objets = load_data_from_backend("http://localhost:5000/data/objets")

#     col1, spacer2, col2 = st.columns([1, 0.2, 3])

#     with col1:
#         st.markdown("<h3>Filtres de Sélection</h3>", unsafe_allow_html=True)
#         if not data_objets.empty:
#             objets_types = data_objets["type_objet"].unique()
#             selected_objets = st.multiselect(
#                 "Sélectionner un ou plusieurs types d'objets",
#                 options=objets_types,
#                 default=objets_types[:1]
#             )
#             granularite = st.selectbox(
#                 "Choisissez la granularité de la période :",
#                 options=["Semaine" ,"Mois", "Année"]
#             )

#     with col2:
#         st.markdown("<h4>Nombre d'Objets Détectés</h4>", unsafe_allow_html=True)
#         if not data_objets.empty:
#             data_objets['date_detection'] = pd.to_datetime(data_objets['date_detection'], errors='coerce')
#             filtered_data_objets = data_objets[data_objets["type_objet"].isin(selected_objets)]

#             if granularite == "Semaine":
#                 filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.to_period('W').astype(str)
#             elif granularite == "Mois":
#                 filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.to_period('M').astype(str)
#             elif granularite == "Année":
#                 filtered_data_objets['periode'] = filtered_data_objets['date_detection'].dt.to_period('Y').astype(str)

#             count_per_period = filtered_data_objets.groupby("periode").size().reset_index(name="Nombre d'objets")

#             fig = px.line(
#                 count_per_period,
#                 x="periode",
#                 y="Nombre d'objets",
#                 labels={"periode": "Période", "Nombre d'objets": "Nombre d'Objets"},
#                 title=f"Nombre d'Objets Détectés par {granularite}"
#             )
#             st.plotly_chart(fig)


# # Fonction pour afficher la satisfaction des utilisateurs
# def afficher_satisfaction():
#     data_satisfaction = load_data_from_backend("http://localhost:5000/data/satisfaction")

#     col1, spacer2, col2 = st.columns([1, 0.2, 3])

#     with col2:
#         st.markdown("<h4>Répartition de la Satisfaction des Utilisateurs</h4>", unsafe_allow_html=True)
#         if not data_satisfaction.empty:
#             total_satisfait = data_satisfaction['satisfait'].sum()
#             total_non_satisfait = data_satisfaction['non_satisfait'].sum()

#             satisfaction_data = pd.DataFrame({
#                 "Catégorie": ["Satisfaits", "Non satisfaits"],
#                 "Valeurs": [total_satisfait, total_non_satisfait]
#             })

#             fig = px.pie(
#                 satisfaction_data,
#                 values="Valeurs",
#                 names="Catégorie",
#                 hole=0.4
#             )
#             st.plotly_chart(fig)


# # Fonction pour afficher la vitesse de détection et le nombre d'objets détectés par période avec filtres
# def afficher_objets_periode():
#     data_objets = load_data_from_backend("http://localhost:5000/data/objets")

#     col1, spacer2, col2 = st.columns([1, 0.2, 3])

#     with col1:
#         st.markdown("<h3>Filtres de Sélection</h3>", unsafe_allow_html=True)
#         if not data_objets.empty:
#             granularite = st.selectbox(
#                 "Choisissez la granularité de la période :",
#                 options=["Semaine", "Mois", "Année"],
#                 key='granularite_periode'
#             )

#     with col2:
#         st.markdown("<h4>Vitesse de Détection et Nombre d'Objets Détectés</h4>", unsafe_allow_html=True)
#         if not data_objets.empty:
#             data_objets['date_detection'] = pd.to_datetime(data_objets['date_detection'], errors='coerce')

#             if granularite == "Semaine":
#                 data_objets['periode'] = data_objets['date_detection'].dt.to_period('W').astype(str)
#             elif granularite == "Mois":
#                 data_objets['periode'] = data_objets['date_detection'].dt.to_period('M').astype(str)
#             elif granularite == "Année":
#                 data_objets['periode'] = data_objets['date_detection'].dt.to_period('Y').astype(str)

#             # Calculer le nombre d'objets détectés par période
#             count_per_period = data_objets.groupby("periode").size().reset_index(name="Nombre d'objets")
            
#             # Calculer le temps moyen de réponse par période
#             response_time_per_period = data_objets.groupby("periode")['temps_reponse'].mean().reset_index(name="Temps Moyen de Réponse (heures)")

#             # Fusionner les deux DataFrame pour avoir le nombre d'objets et le temps de réponse moyen dans une seule table
#             merged_data = pd.merge(count_per_period, response_time_per_period, on="periode")

#             # Affichage du graphique
#             fig = px.line(
#                 merged_data,
#                 x="periode",
#                 y=["Nombre d'objets", "Temps Moyen de Réponse (heures)"],
#                 labels={"periode": "Période", "value": "Valeur", "variable": "KPI"},
#                 title=f"Nombre d'Objets et Temps Moyen de Réponse par {granularite}"
#             )
#             st.plotly_chart(fig)


# # Appel des fonctions d'affichage
# afficher_objets()
# afficher_satisfaction()
# afficher_objets_periode()
