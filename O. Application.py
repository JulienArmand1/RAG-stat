
import os
import pandas as pd
import numpy as np
from langchain_openai.embeddings import OpenAIEmbeddings
import google.generativeai as genai
import gradio as gr
from transformers import pipeline
from openai import OpenAI
client = OpenAI()

def recherche_chunk(embeddings,prompt,k):
    embed = OpenAIEmbeddings()
    c=np.array(embed.embed_query(prompt))
    calcul_similarite = np.dot(embeddings,c)

    index = sorted(range(len(calcul_similarite)), key=lambda i: calcul_similarite[i], reverse=True)
    liste_chunk=[]
    for i in index[0:k]:
            liste_chunk.append(i)
    return liste_chunk

def gemini(prompt):
    try:
        genai.configure(api_key=os.environ["google_key"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"


def reponse(nbs_chunk,texte):
    prompt = texte
    z = recherche_chunk(arr,prompt,nbs_chunk)
    print(z)
    resu = chunks.loc[z]
    txt=""
    for i in resu["chunks"]:
        txt=txt+"/"+i
    a = gemini("Répond succinctement à la question suivante"+prompt+" avec ces chunks de rag (n'invente rien')"+txt)


    b = gemini(f"Mets toi dans la peau d'un amateur de statistique et Évalue la réponse d'un outil de RAG: {a} au prompt suivant {texte}. Est-ce que l'utilisateur sera satisfait. Écris un court texte.")
    distilled_student_sentiment_classifier = pipeline(
        model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
        return_all_scores=True
    )
    c=distilled_student_sentiment_classifier(b[0:512])
    score = str((c[0][0]["score"])*100//1)

    ff=set()
    for f in resu["lien"]:
        ff.add(f)
    print(ff)
    lien_txt = ""
    for lien in ff :
        lien_txt = lien_txt + lien + "\n"

    return [a,txt,lien_txt,b,score]


if __name__ == "__main__":

    # Importation des chunks
    imput_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2"
    path_data = os.path.join(imput_dir, "I2. Chunk_mod.xlsx")
    chunks = pd.read_excel(path_data)
    print("done1")

    # Importation des embeddings
    input_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2"
    path_data = os.path.join(input_dir, "L2. Embeddings.csv")
    arr = np.loadtxt(path_data, delimiter=",")
    print("done2")

    # Essai 1
    demo = gr.Interface(
        fn=reponse,
        inputs=[gr.Slider(2, 200, value=4, label="Nbs_chunks", info="Nombre de chunks entre 2 and 20", step=1),gr.Textbox(label="Entrée")],
        outputs=[
            gr.Textbox(label="Résultat"),
            gr.Textbox(label="Chunks"),
            gr.Textbox(label="Liste des liens utiles à la recherche"),
            gr.Textbox(label="Évaluation AI 1"),
            gr.Textbox(label="Évaluation AI")]
    )

    demo.launch()