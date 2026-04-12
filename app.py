import streamlit as st
import pandas as pd
import os
from main import clone_repository, get_file_stats, analyze_data, visualize_data, ask_ai_for_report, REPO_URL, TARGET_DIR, EXTENSIONS

st.set_page_config(page_title="Repo Architect AI", layout="wide")

st.title("Repo Architect - Analyse d'Architecture IA")
st.markdown("---")

# --- SIDEBAR (CONFIGURATION) ---
st.sidebar.header("Configuration")
repo_input = st.sidebar.text_input("URL du Dépôt (SSH)", value=REPO_URL)
target_path = st.sidebar.text_input("Dossier de destination", value=TARGET_DIR)

if st.sidebar.button("Lancer l'Analyse"):
    with st.spinner("Clonage et analyse en cours..."):
        # 1. Clonage
        if os.path.exists(target_path):
             import shutil
             shutil.rmtree(target_path) # On nettoie pour être sûr d'avoir le dernier code
        
        clone_repository(repo_input, target_path)
        
        # 2. Collecte des données
        df = get_file_stats(target_path)
        
        if not df.empty:
            # Layout en colonnes
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Répartition du Code")
                summary, top_5 = analyze_data(df)
                st.dataframe(df.drop(columns=['path']).head(10)) # On montre un extrait
                
                # Top 5
                st.write("**Top 5 des fichiers les plus longs :**")
                st.table(top_5)

            with col2:
                st.subheader("Visualisation")
                import matplotlib.pyplot as plt
                import seaborn as sns
                
                # On regénère le graphique pour Streamlit
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.barplot(x=summary.index, y=summary.values, palette="viridis", ax=ax)
                plt.title("Lignes par langage")
                st.pyplot(fig)

            # 3. Analyse IA
            st.markdown("---")
            st.subheader("Rapport de l'Architecte IA (Ollama)")
            
            top_file = df.nlargest(1, 'lines')['path'].values[0]
            st.info(f"Analyse du fichier principal : `{top_file}`")
            
            # On détourne print pour capturer la réponse (ou on modifie ask_ai_for_report)
            # Pour faire simple ici, on va juste rappeler ollama directement ou
            # s'assurer que ask_ai_for_report est dispo.
            
            try:
                import ollama
                with open(f"{target_path}/{top_file}", 'r') as f:
                    code_content = f.read()[:2000]
                
                prompt = f"Analyse ce fichier : {top_file}. Donne 3 points d'amélioration prioritaires (Performance, Lisibilité, Architecture). Réponds en français."
                
                response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': prompt}])
                st.success(response['message']['content'])
                
            except Exception as e:
                st.error(f"Erreur IA : {e}")

        else:
            st.warning("Aucun fichier de code trouvé dans ce dépôt.")
else:
    st.info("Entrez une URL de dépôt SSH dans la barre latérale et cliquez sur 'Lancer l'Analyse'.")
