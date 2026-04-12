import streamlit as st
import pandas as pd
import os
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
import ollama
from main import clone_repository, get_file_stats, analyze_data, REPO_URL, TARGET_DIR

st.set_page_config(page_title="Repo Architect AI", layout="wide")

st.title("Repo Architect - Analyse d'Architecture IA")
st.markdown("---")

# --- INITIALISATION DU STATE (Mémoire de l'application) ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'top_5' not in st.session_state:
    st.session_state.top_5 = None
if 'target_path' not in st.session_state:
    st.session_state.target_path = None

# --- SIDEBAR (CONFIGURATION) ---
st.sidebar.header("Configuration")
repo_input = st.sidebar.text_input("URL du Dépôt (SSH)", value=REPO_URL)
target_path_input = st.sidebar.text_input("Dossier de destination", value=target_path_input if 'target_path' in locals() else TARGET_DIR)

if st.sidebar.button("Lancer l'Analyse"):
    with st.spinner("Clonage et analyse en cours..."):
        # Nettoyage et Clonage
        if os.path.exists(target_path_input):
             shutil.rmtree(target_path_input)
        
        clone_repository(repo_input, target_path_input)
        
        # Collecte des données
        df = get_file_stats(target_path_input)
        
        if not df.empty:
            summary, top_5 = analyze_data(df)
            # Sauvegarde dans le state pour éviter de tout perdre au prochain clic
            st.session_state.df = df
            st.session_state.summary = summary
            st.session_state.top_5 = top_5
            st.session_state.target_path = target_path_input
        else:
            st.error("Aucun fichier de code trouvé dans ce dépôt.")

# --- AFFICHAGE DES RÉSULTATS (SI DISPONIBLES DANS LE STATE) ---
if st.session_state.df is not None:
    df = st.session_state.df
    summary = st.session_state.summary
    top_5 = st.session_state.top_5
    target_path = st.session_state.target_path

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(" Répartition du Code")
        st.dataframe(df.drop(columns=['path']).head(10), use_container_width=True)
        st.write("**Top 5 des fichiers les plus longs :**")
        st.table(top_5)

    with col2:
        st.subheader("Visualisation")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=summary.index, y=summary.values, palette="viridis", ax=ax)
        plt.title("Lignes par langage")
        st.pyplot(fig)

    # --- ANALYSE IA ---
    st.markdown("---")
    st.subheader("Rapport de l'Architecte IA (Ollama)")
    
    audit_mode = st.radio("Mode d'analyse :", ["Fichier principal uniquement", "Audit Global (Projet complet)"], key="audit_mode_radio")

    if st.button("Générer le rapport IA"):
        if audit_mode == "Fichier principal uniquement":
            top_file = df.nlargest(1, 'lines')['path'].values[0]
            st.info(f"Analyse du fichier principal : `{top_file}`")
            try:
                with open(os.path.join(target_path, top_file), 'r', encoding='utf-8', errors='ignore') as f:
                    code_content = f.read()[:2000]
                prompt = f"Analyse ce fichier : {top_file}. Donne 3 points d'amélioration prioritaires (Performance, Lisibilité, Architecture). Réponds brièvement en français."
                response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': prompt}])
                st.success(response['message']['content'])
            except Exception as e:
                st.error(f"Erreur IA : {e}")
        
        else:
            st.info("Analyse de l'architecture globale en cours...")
            file_list = df['path'].tolist()
            top_files_data = ""
            for _, row in df.nlargest(5, 'lines').iterrows():
                try:
                    with open(os.path.join(target_path, row['path']), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()[:1000]
                        top_files_data += f"\n--- FICHIER: {row['path']} ---\n{content}\n"
                except: continue

            global_prompt = f"Analyse la structure de ce projet.\nLISTE DES FICHIERS :\n{file_list}\nEXTRAITS DES FICHIERS CLÉS :\n{top_files_data}\nRéponds brièvement en français sur : 1. Cohérence de la structure 2. Risques identifiés 3. Recommandation prioritaire."
            
            try:
                with st.status("L'IA analyse le projet complet..."):
                    response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': global_prompt}])
                st.success(response['message']['content'])
            except Exception as e:
                st.error(f"Erreur audit global : {e}")
else:
    st.info("Entrez une URL de dépôt SSH dans la barre latérale et cliquez sur 'Lancer l'Analyse'.")
