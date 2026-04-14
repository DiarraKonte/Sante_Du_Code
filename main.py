import git
import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import ollama
from radon.complexity import cc_visit

# --- CONFIGURATION ---
REPO_URL = "git@github.com:DiarraKonte/Sante_Du_Code.git"
TARGET_DIR = "./data/cloned_repo"
IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', 'venv', 'dist', 'build', '.venv'}
EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.css', '.html', '.go', '.java', '.md'}

def get_complexity(content, extension):
    """calcule la complexite cyclomatique moyenne pour les fichiers supportes."""
    if extension != '.py':
        return 0 # Pour l'instant on se concentre sur Python pour la complexité brute
    try:
        results = cc_visit(content)
        if not results:
            return 0
        return sum(r.complexity for r in results) / len(results)
    except:
        return 0

def clone_repository(url, target):
    """Clone le repo s'il n'existe pas deja sur PC."""
    if not os.path.exists(target):
        os.makedirs(os.path.dirname(target), exist_ok=True)
        print(f"--- Clonage de {url} en cours... ---")
        try:
            git.Repo.clone_from(url, target)
            print("--- Clonage terminé ! ---")
        except Exception as e:
            print(f"Erreur lors du clonage : {e}")
            raise e
    else:
        print("--- Repo deja present localement ---")

def get_file_stats(repo_path):
    """Parcourt le repo et extrait les données."""
    stats = []
    path_obj = Path(repo_path)

    for file_path in path_obj.rglob('*'):
        if any(ignored in file_path.parts for ignored in IGNORE_DIRS):
            continue

        if file_path.is_file() and file_path.suffix in EXTENSIONS:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.splitlines()
                    complexity = get_complexity(content, file_path.suffix)
                    
                    stats.append({
                        'filename': file_path.name,
                        'extension': file_path.suffix,
                        'lines': len(lines),
                        'complexity': round(complexity, 2),
                        'size_kb': os.path.getsize(file_path) / 1024,
                        'path': str(file_path.relative_to(repo_path))
                    })
            except Exception as e:
                print(f"Erreur lecture {file_path}: {e}")

    return pd.DataFrame(stats)

def analyze_data(df):
    """analyse les donnees avec Pandas."""
    print("\n--- ANALYSE DES DONNEES ---")
    summary = df.groupby('extension')['lines'].sum().sort_values(ascending=False)
    top_5 = df.nlargest(5, 'lines')[['filename', 'lines', 'complexity']]
    return summary, top_5

def visualize_data(summary):
    """Génère un graphique de répartition."""
    print("\n--- GENERATION DU GRAPHIQUE ---")
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(x=summary.index, y=summary.values, palette="viridis")
    plt.title("Répartition des lignes de code par langage")
    plt.xlabel("Extension")
    plt.ylabel("Nombre de lignes")
    
    os.makedirs("output", exist_ok=True)
    output_path = "output/report.png"
    plt.savefig(output_path)
    print(f"Graphique sauvegardé dans : {output_path}")
    plt.close()

def ask_ai_for_report(top_file_path):
    """utilisation de ollama mistral 8B pour analyser les fichiers, le modele est en local"""
    print("\n APPEL À L'IA (Ollama)")
    try:
        with open(f"{TARGET_DIR}/{top_file_path}", 'r', encoding='utf-8', errors='ignore') as f:
            code_content = f.read()[:2000]
            
        prompt = f"Analyse ce fichier : {top_file_path}. Donne 3 points d'amélioration. Réponds en français."
        response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': prompt}])
        print("\nConseils de l'Architecte IA :")
        print(response['message']['content'])
    except Exception as e:
        print(f"Erreur avec Ollama : {e}")

if __name__ == "__main__":
    # Point d'entrée principal pour l'utilisation en ligne de commande
    clone_repository(REPO_URL, TARGET_DIR)
    df_stats = get_file_stats(TARGET_DIR)
    
    if not df_stats.empty:
        summary, top_5 = analyze_data(df_stats)
        visualize_data(summary)
        
        top_file = df_stats.nlargest(1, 'lines')['path'].values[0]
        ask_ai_for_report(top_file)
    else:
        print("Aucune donnée trouvée.")
