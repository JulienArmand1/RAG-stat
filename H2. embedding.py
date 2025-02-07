import pandas as pd
from langchain_openai.embeddings import OpenAIEmbeddings
import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
client = OpenAI()

# Transformation des chunks en embedding
def chunks_to_embedding(liste_chunks,taille_batch):
    embed = OpenAIEmbeddings()
    liste_chunks = [str(i) for i in liste_chunks]
    vector = np.array(embed.embed_documents([liste_chunks[0]]))
    for i in range(1,len(liste_chunks),taille_batch):
        print(i)
        progres = int(100*i/len(liste_chunks))
        print(f"Progression : {progres} %")
        vector2 = np.array(embed.embed_documents(liste_chunks[i:i+taille_batch]))
        print(vector.shape)
        print(vector2.shape)
        vector = np.vstack((vector, vector2))
    return vector


if __name__ == "__main__":

    # Merge des datasets
    imput_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2"
    path_data = os.path.join(imput_dir, "G2. table_chunks.xlsx")
    chunks = pd.read_excel(path_data)
    path_equiv = os.path.join(imput_dir, "C. Equivalence_complete.xlsx")
    equiv = pd.read_excel(path_equiv)
    equiv['fichier'] = equiv['nom_après_separation'].str.replace('.pdf', '')
    df_left = pd.merge(chunks, equiv, on='fichier', how='left')
    df_left.drop(['Unnamed: 0_x', 'Unnamed: 0_y'], axis='columns', inplace=True)

    chemin_df = os.path.join(imput_dir, "I2.Chunk_mod.xlsx")
    df_left.to_excel(chemin_df)

    output_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2\H2. embeddings"
    for annee in range(2008,2025):
        path = os.path.join(imput_dir, "A. pdf", str(annee))
        if os.path.isdir(path):
            vector = chunks_to_embedding(list(df_left[df_left['fichier'].str.contains(str(annee))]['chunks']), 500)
            np.savetxt('array.txt', vector)
            path2 = os.path.join(output_dir, str(annee)+".csv")
            np.savetxt(path2, vector, delimiter=',',fmt='%.18f')