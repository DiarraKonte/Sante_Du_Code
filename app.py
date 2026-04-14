import streamlit as st
import pandas as pd
import os
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import ollama
from main import clone_repository, get_file_stats, analyze_data, REPO_URL, TARGET_DIR

st.set_page_config(page_title="Repo Architect AI", layout="wide")

st.title("Repo Architect AI")
st.markdown("""
> **Audit d'architecture intelligent**  
> Cet outil analyse la structure de vos projets, calcule la complexité technique et utilise une IA locale pour identifier la dette technique.
""")
st.markdown("---")
st.markdown("*Projet réalisé dans le cadre d'un auto-apprentissage sur l'intégration des LLMs et l'analyse de données logicielle.*")

# INITIALISATION DU STATE
if 'df' not in st.session_state:
    st.session_state.df = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'top_5' not in st.session_state:
    st.session_state.top_5 = None
if 'target_path' not in st.session_state:
    st.session_state.target_path = None

# SIDEBAR
st.sidebar.header("Configuration")
repo_input = st.sidebar.text_input("URL du Dépôt (SSH)", value=REPO_URL)
target_path_input = st.sidebar.text_input("Dossier de destination", value=TARGET_DIR)

if st.sidebar.button("Lancer l'Analyse"):
    with st.spinner("Clonage, calcul de complexité et analyse en cours..."):
        if os.path.exists(target_path_input):
             shutil.rmtree(target_path_input)
        
        clone_repository(repo_input, target_path_input)
        df = get_file_stats(target_path_input)
        
        if not df.empty:
            summary, top_5 = analyze_data(df)
            st.session_state.df = df
            st.session_state.summary = summary
            st.session_state.top_5 = top_5
            st.session_state.target_path = target_path_input
        else:
            st.error("Aucun fichier de code trouvé.")

if st.session_state.df is not None:
    df = st.session_state.df
    summary = st.session_state.summary
    top_5 = st.session_state.top_5
    target_path = st.session_state.target_path

    # KPI TOP
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Lignes", f"{df['lines'].sum():,}")
    c2.metric("Fichiers", len(df))
    c3.metric("Complexité Moyenne", f"{df[df['complexity'] > 0]['complexity'].mean():.2f}")

    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Répartition & Complexité")
        st.dataframe(df[['filename', 'lines', 'complexity', 'extension']].sort_values('complexity', ascending=False).head(10), use_container_width=True)
        
    with col2:
        st.subheader("Treemap du Projet")
        # Treemap : Taille = Lignes, Couleur = Complexité
        fig = px.treemap(df, path=[px.Constant("all"), 'extension', 'filename'], 
                         values='lines',
                         color='complexity',
                         color_continuous_scale='RdYlGn_r',
                         hover_data=['path'])
        st.plotly_chart(fig, use_container_width=True)

    # ANALYSE IA 
    st.markdown("---")
    st.subheader("Audit de l'Architecte IA (Ollama Mistral 8B)")
    
    audit_mode = st.radio("Cible de l'audit :", ["Points critiques (Complexité)", "Structure Globale"], horizontal=True)

    if st.button("Générer le rapport d'expertise"):
        if audit_mode == "Points critiques (Complexité)":
            # On prend le fichier le plus complexe
            top_complex = df.nlargest(1, 'complexity')
            if not top_complex.empty:
                file_path = top_complex['path'].values[0]
                compl = top_complex['complexity'].values[0]
                st.info(f"Analyse du fichier le plus complexe : `{file_path}` (Score: {compl})")
                
                try:
                    with open(os.path.join(target_path, file_path), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()[:3000]
                    
                    prompt = f"""Tu es un Senior Architect. Analyse ce code source ({file_path}) qui a une complexité cyclomatique de {compl}.
                    1. Identifie les 2 'Code Smells' les plus graves.
                    2. Propose une refactorisation concrète pour réduire la complexité.
                    Réponds de manière technique et concise en français.
                    
                    CODE:
                    {content}"""
                    
                    with st.status("L'IA examine le code..."):
                        response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': prompt}])
                    st.success(response['message']['content'])
                except Exception as e:
                    st.error(f"Erreur IA : {e}")
        
        else:
            st.info("Audit de la structure et des dépendances...")
            file_tree = df[['path', 'lines', 'complexity']].to_string(index=False)
            
            global_prompt = f"""Tu es un CTO expert en audit. Voici la structure d'un projet Git (Chemin, Lignes, Complexité) :
            {file_tree[:2000]}
            
            Analyse cette architecture et réponds sur :
            1. Un risque majeur identifié (ex: God Object, manque de modularité).
            2. Une recommandation stratégique pour l'équipe de dev.
            Réponds brièvement et professionnellement en français."""
            
            try:
                with st.status("Audit architectural en cours..."):
                    response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': global_prompt}])
                st.success(response['message']['content'])
            except Exception as e:
                st.error(f"Erreur audit : {e}")
else:
    st.info("Configurez le dépôt SSH à gauche pour démarrer l'audit.")
