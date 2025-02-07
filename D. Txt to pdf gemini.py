import os
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import time as time

from PyPDF2 import PdfReader

def is_valid_pdf(file_path):
    try:
        PdfReader(file_path)
        return True
    except Exception:
        return False


def pdf_to_text(instruction):
    name = instruction[0]
    path = instruction[1]

    output_dir = instruction[2]

    print(name)

    prompt = """
    Transforme l'intégralité du contenu du PDF en texte en suivant une approche étape par étape pour assurer une extraction précise.
    1. Lis et comprends chaque section du PDF.
    2. Transforme le texte fidèlement, en veillant à ne rien ajouter ni omettre.
    3. Pour les images et graphiques, analyse chaque élément et extrais tout ce qui possible.
       Tu peux décrire en quelques phrases les éléments les plus important que tu observes sur des graphiques
       tout en restant très neutre.
    4. Lorsque tu rencontres des tableaux, formate-les pour avoir savoir pour chaque nombre ce qu'il représente.
    5. Vérifie chaque étape pour t'assurer que toutes les informations sont correctement extraites et formatées.

    ### Exemples :

    Exemple 1 :
    - Contenu PDF : "50% des Canadiens sont satisfaits."
    - Extraction attendue : "50% des Canadiens sont satisfaits."

    Exemple 2 :
    - Contenu PDF : Un tableau avec deux colonnes.
    | Diplôme universitaire|
    | Âge | Pourcentage |
    | 18-24 | 35% |
    | 25-34 | 40% |
    Extraction attendue :
    - Âge : 18-24 Pourcentage : 35% Diplôme universaire
    - Âge : 25-34 Pourcentage : 40% Diplôme universaire

    Exemple 3 :
    - Contenu PDF : Une image avec un drapeau canadien avec le texte "Statistique Canada"
    - Extraction attendue :
        "Statistique Canada"
        "Description: Un drapeau canadien est aussi présent sur l'image"

    ### Instructions :
    Maintenant, applique ce processus pour le PDF fourni. Assure-toi qu'aucune information n'est altérée ou perdue lors de la conversion.
    """

    for essai in range(3):
        if is_valid_pdf(path):
            try:
                genai.configure(api_key=os.environ["google_key"])
                model = genai.GenerativeModel("gemini-1.5-flash")

                pdf = genai.upload_file(path)
                response = model.generate_content([prompt, pdf])
                output_path = os.path.join(output_dir, name.replace('.pdf', ''))
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                return [str(name), "succès"]
            except Exception as e:
                print(f"Essai {essai + 1} pour {name}: {e}")
                time.sleep(2)
    return [str(name), "fail"]


if __name__ == "__main__":

    input_dir = r"C:\Users\14388\Desktop\Projet de session\pdf v6 mod"
    output_dir = r"C:\Users\14388\Desktop\Projet de session\txt v6"

    instructions = []
    for name in os.listdir(input_dir):
        path = os.path.join(input_dir, name)
        instructions = instructions+([name, path, output_dir])

    resu = []
    with ThreadPoolExecutor(max_workers=100) as executor:
         results = list(executor.map(pdf_to_text, instructions))

    df = pd.DataFrame(results, columns =['lien', 'resultat'])
    chemin_df = os.path.join(output_dir, "Resultat_gemini.xlsx")
    df.to_excel(chemin_df)