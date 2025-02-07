
import os
import pandas as pd
import numpy as np
from langchain_openai.embeddings import OpenAIEmbeddings
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai
from transformers import pipeline
import pyttsx3
import ollama
from openai import OpenAI
client = OpenAI()

def recherche_chunk(embeddings,prompt,k):
    embed = OpenAIEmbeddings()
    c=np.array(embed.embed_query(prompt))
    calcul_similarite = np.dot(embeddings,c)
    index = sorted(range(len(calcul_similarite)), key=lambda i: calcul_similarite[i], reverse=True)
    return index[0:k]

def gemini(prompt):
    try:
        genai.configure(api_key=os.environ["google_key"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

def gpt4o(prompt):
    try:
        completion = client.chat.completions.create(
          model="gpt-4o",
          messages=[
            {"role": "system", "content": "You are an assistant, skilled and super smart. You should retrive information. If you don't find anything, don't try to invent somethings"},
            {"role": "user", "content": prompt}
          ]
        )
        return str(completion.choices[0].message.content)
    except Exception as e:
        return f"Error: {e}"

def llama(prompt):
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        print(response["message"]["content"])
        return response["message"]["content"]
    except Exception as e:
        return f"Error: {e}"


def reponse(info):

    nbs_chunk = info[0]
    prompt = info[1]
    fichier = info[2]
    choix_prompt = info[3]
    choix_modele = info[4]

     # Recherche des chunks
    if nbs_chunk > 0:
        z = recherche_chunk(arr,prompt,nbs_chunk)
        resu = chunks.loc[z]
        txt=""
        for i in resu["chunks"]:
            txt=txt+str(i)
    else:
        txt=""

    # Préparation des prompts
    if nbs_chunk > 0:
        if choix_prompt == "court":
            prompt2 = "Répond succinctement à la question suivante"+prompt+" avec ces chunks de rag (n'invente rien')"+txt
        if choix_prompt == "long":
            prompt2 = "Répond à la question suivante en fournissant une analyse détaillée intéressante à lire"+prompt+" avec ces chunks de rag (n'invente rien')"+txt
    else:
        if choix_prompt == "court":
            prompt2 = "Répond Succinctement à la question suivante"+prompt+" avec des connaissances dont tu es absolument certain (n'invente rien')"+txt
        if choix_prompt == "long":
            prompt2 = "Répond à la question suivante en fournissant une analyse détaillée intéressante à lire"+prompt+" avec des connaissances dont tu es absolument certain (n'invente rien')"+txt

    # Appel du Générateur
    if choix_modele == "llama":
        a = llama(prompt2)
    if choix_modele == "gemini":
        a = gemini(prompt2)
    if choix_modele == "gpt4o":
        a = gpt4o(prompt2)

    # Évaluation pour les fichiers
    if nbs_chunk > 0:
        ff=set()
        for f in resu["nom_avant_separation"]:
            ff.add(f)
        if fichier in ff:
            indicatrice_bon_fichier = 1
        else:
            indicatrice_bon_fichier = 0
        nbs_doc = len(ff)
    else:
        indicatrice_bon_fichier = 0
        nbs_doc = 0

    # Évaluation par analyseur de sentiment
    b = gemini(f"Mets toi dans la peau d'un amateur de statistique et évalue la réponse d'un outil de RAG: {a} au prompt suivant {prompt}. Est-ce que l'utilisateur sera satisfait. Écris un court texte.")
    c=distilled_student_sentiment_classifier(b[0:512])
    score = str((c[0][0]["score"])*100//1)

    return [score,indicatrice_bon_fichier,nbs_doc]


if __name__ == "__main__":

    # Importation des chunks
    imput_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2"
    path_data = os.path.join(imput_dir, "I. Chunk_mod.xlsx")
    chunks = pd.read_excel(path_data)

    # Importation des embeddings
    input_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2"
    path_data = os.path.join(input_dir, "L. Embeddings.csv")
    arr = np.loadtxt(path_data, delimiter=",")

    # Importation de l'analyse de positivité du texte
    distilled_student_sentiment_classifier = pipeline(
        model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
        return_all_scores=True
    )

    # Importation des questions
    analyse_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2\M. Analyse"
    path_data = os.path.join(analyse_dir, "Test 1.xlsx")
    question = pd.read_excel(path_data)


    nbs_chunks = [0]+[2**i for i in range(9)]
    resu1 = []
    resu2 = []
    resu3 = []
    for index, row in question.iterrows():
        texte = row['Questions']
        fichier = row['Fichier']

        list_nbs_chunks =(
            [[i,texte,fichier,"court","llama"] for i in nbs_chunks]+
            [[i,texte,fichier,"long","llama"] for i in nbs_chunks]+
            [[i,texte,fichier,"court","gemini"] for i in nbs_chunks]+
            [[i,texte,fichier,"long","gemini"] for i in nbs_chunks]+
            [[i,texte,fichier,"court","gpt4o"] for i in nbs_chunks]+
            [[i,texte,fichier,"long","gpt4o"] for i in nbs_chunks]
            )
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(reponse, list_nbs_chunks))
            resu1.append([scores[0] for scores in results])
            resu2.append([indicatrices[1] for indicatrices in results])
            resu3.append([longueur[2] for longueur in results])

    engine = pyttsx3.init()
    engine.say("Hello, The results are in !")
    engine.runAndWait()

    array1 = np.array(resu1)
    array2 = np.array(resu2)
    array3 = np.array(resu3)

    columns = (
        ["court_"+"llama_"+str(i) for i in nbs_chunks]+
        ["long_"+"llama_"+str(i) for i in nbs_chunks]+
        ["court_"+"gemini_"+str(i) for i in nbs_chunks]+
        ["long_"+"gemini_"+str(i) for i in nbs_chunks]+
        ["court_"+"gpt4o_"+str(i) for i in nbs_chunks]+
        ["long_"+"gpt4o_"+str(i) for i in nbs_chunks]
        )

    df1 = pd.DataFrame(array1, columns=columns)
    df1.to_excel(os.path.join(analyse_dir, 'analyse100_score_test2.xlsx'), index=False)

    df2 = pd.DataFrame(array2, columns=columns)
    df2.to_excel(os.path.join(analyse_dir, 'analyse100_indicatrice_test2.xlsx'), index=False)

    df3 = pd.DataFrame(array3, columns=columns)
    df3.to_excel(os.path.join(analyse_dir, 'analyse100_longueur_test2.xlsx'), index=False)