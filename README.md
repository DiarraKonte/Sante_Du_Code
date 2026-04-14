# Repo Architect AI

> **Repo Architect AI** est un outil simple pour faire un audit rapide de tes projets Git. Le script récupère tes fichiers, sort des stats avec **Pandas** et demande à une **IA locale de ton choix(Ollama)** de te donner des conseils d'architecture.

<div align="center">
  <video src="assets/demo.mp4" width="100%" controls autoplay loop muted></video>
</div>

---

## Aperçu
*Une analyse 100% locale et rapide de vos dépôts Git.*

**Repo Architect AI** est parfait pour voir en un coup d'œil la santé d'un repo et avoir un avis d'expert (IA) sur ton code sans rien envoyer sur le Cloud. L'analyse pourrais etre pousser plus loin avec une IA plus performante.

---

## Ce qu'il y a dedans
- **Analyse de données** : Utilisation de **Pandas** pour calculer le nombre de lignes et la taille des fichiers.
- **Visualisation** : Graphiques avec **Seaborn** pour voir la répartition des langages.
- **IA Locale (Souveraine)** : Intégration d'**Ollama** avec le modèle **Mistral 8B**.
- **Interface Web** : Dashboard interactif fait avec **Streamlit**.

---

## Comment l'utiliser (avec ton IA locale)

L'avantage de ce projet, c'est qu'il tourne à 100% sur ta machine. Pas besoin de clé API payante (OpenAI/Anthropic).

### 1. Préparer l'IA (Ollama)
Tu dois avoir [Ollama](https://ollama.com/) installé. Pour récupérer le modèle utilisé par le projet :
```bash
ollama pull mistral
```
*(Assure-toi qu'Ollama tourne en arrière-plan avant de lancer l'app).*

### 2. Installation du projet
```bash
git clone git@github.com:DiarraKonte/repo-architect.git
cd repo-architect

# Creer l'environnement virtuel et installer les outils
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Lancer l'analyse
Pour ouvrir l'interface dans ton navigateur :
```bash
streamlit run app.py
```

---

## Comment ça marche ?

1. **Clonage** : Tu donnes l'URL SSH d'un repo, et le script le clone dans un dossier temporaire de ton choix.
2. **Stats** : Le script scanne tout le projet (en ignorant les dossiers inutiles a l'analyse comme `node_modules` ou `.git`).
3. **Audit IA** : 
   - **Mode Fichier** : L'IA analyse le fichier le plus gros ou les 5 plus gros fichiers pour trouver des bugs ou des soucis de performance. Encopre une fois l'analyse pourrais etre pousser plus loin avec des IA plus performantes.
   - **Mode Global** : L'IA regarde toute l'arborescence du projet pour te dire si ton architecture tient la route.

---

## Pourquoi ce projet ?
Premierememt : je voulais un outil pour m'aider a faire des audits rapides de mes projets, c'est quelque chose que je demandais beaucoup a claude Code, l'avoir comme ca m'evite de bruler des tokens.
Deuxiemement : je voulais m'entraîner à manipuler des pipelines de données (Data Engineering) et à intégrer des **LLM locaux** dans des outils. C'est un bon exemple de ce qu'on peut faire en mélangeant Python, la Data et l'IA.

---
**Fait par [Diarra Konte](https://github.com/DiarraKonte)**  
*En recherche d'alternance en Dev Data / Data IA.*
