import git
import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import ollama

# --- CONFIGURATION ---
REPO_URL = "git@github.com:DiarraKonte/Sante_Du_Code.git"
TARGET_DIR = "./data/cloned_repo"
IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', 'venv', 'dist', 'build'}
EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.css', '.html', '.go', '.java'}

def clone_repository(url, target):
    """Clone le repo s'il n'existe pas déjà sur ton PC."""
    if not os.path.exists(target):
        print(f"--- Clonage de {url} en cours... ---")
        try:
            git.Repo.clone_from(url, target)
            print("--- Clonage terminé ! ---")
        except Exception as e:
            print(f"Erreur lors du clonage : {e}")
    else:
        print("--- Repo déjà présent localement. ---")

def get_file_stats(repo_path):
    """
    Parcourt le repo et extrait les données.
    ETAPE DATA : On transforme du texte en DataFrame Pandas.
    """
    stats = []
    path_obj = Path(repo_path)

    for file_path in path_obj.rglob('*'):
        if any(ignored in file_path.parts for ignored in IGNORE_DIRS):
            continue

        if file_path.is_file() and file_path.suffix in EXTENSIONS:
            try:
                # On lit les fichiers pour compter les lignes
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    stats.append({
                        'filename': file_path.name,
                        'extension': file_path.suffix,
                        'lines': len(lines),
                        'size_kb': os.path.getsize(file_path) / 1024,
                        'path': str(file_path.relative_to(repo_path))
                    })
            except Exception as e:
                print(f"Erreur lecture {file_path}: {e}")

    return pd.DataFrame(stats)

def analyze_data(df):
    """
    Utilise Pandas pour sortir des insights rapides.
    """
    print("\n--- ANALYSE DES DONNÉES ---")
    # Groupement par extension pour voir la répartition du code
    summary = df.groupby('extension')['lines'].sum().sort_values(ascending=False)
    print("Répartition des lignes par langage :")
    print(summary)
    
    # Top 5 des fichiers les plus gros
    top_5 = df.nlargest(5, 'lines')[['filename', 'lines']]
    print("\nTop 5 des fichiers les plus volumineux :")
    print(top_5)
    
    return summary, top_5

def visualize_data(summary):
    """
    ETAPE DATA VIZ : Transforme les chiffres en graphique parlant.
    """
    print("\n--- GÉNÉRATION DU GRAPHIQUE ---")
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    # Création du barplot
    ax = sns.barplot(x=summary.index, y=summary.values, palette="viridis")
    
    plt.title("Répartition des lignes de code par langage")
    plt.xlabel("Extension")
    plt.ylabel("Nombre de lignes")
    
    # Sauvegarde du graphique
    output_path = "output/report.png"
    plt.savefig(output_path)
    print(f"Graphique sauvegardé dans : {output_path}")
    plt.close()

def ask_ai_for_report(top_file_path):
    """
    ETAPE IA : Utilise Ollama pour donner un conseil sur le code.
    """
    print("\n--- APPEL À L'IA (Ollama) ---")
    
    try:
        # Lecture du fichier pour donner le contexte à l'IA
        with open(f"{TARGET_DIR}/{top_file_path}", 'r') as f:
            code_content = f.read()[:2000] # On limite pour ne pas saturer l'IA
            
        prompt = f"""
        En tant qu'architecte logiciel expert, analyse ce fichier : {top_file_path}.
        Voici un extrait du code :
        ---
        {code_content}
        ---
        Quels sont les 3 points d'amélioration prioritaires pour ce fichier (performance, lisibilité ou architecture) ? Réponds brièvement en français.
        """
        
        response = ollama.chat(model='mistral', messages=[
            {'role': 'user', 'content': prompt},
        ])
        
        print("\nConseils de l'Architecte IA :")
        print(response['message']['content'])
        
    except Exception as e:
        print(f"Erreur avec Ollama : {e}. Assure-toi d'avoir fait 'ollama pull mistral' et que le serveur tourne.")

if __name__ == "__main__":
    clone_repository(REPO_URL, TARGET_DIR)
    df_stats = get_file_stats(TARGET_DIR)
    
    if not df_stats.empty:
        summary, top_5 = analyze_data(df_stats)
        visualize_data(summary)
        
        # On analyse le fichier n°1 avec l'IA
        top_file = df_stats.nlargest(1, 'lines')['path'].values[0]
        ask_ai_for_report(top_file)
    else:
        print("Aucune donnée trouvée.")
