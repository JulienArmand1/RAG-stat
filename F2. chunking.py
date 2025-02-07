
import pandas as pd
from langchain_text_splitters import CharacterTextSplitter
import os


text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=10)

# Chunking
def chunking(input_dir):
    chunks = []
    for name in os.listdir(input_dir):
        print(name)
        path = os.path.join(input_dir, name)
        with open(path, encoding='utf-8') as f:
            text = f.read()
        text_temp = text_splitter.create_documents([text])
        ajout = [[name, chunk.page_content] for chunk in text_temp]
        chunks = chunks + ajout
    return chunks


if __name__ == "__main__":
    input_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2\F. txt"
    chunks = chunking(input_dir)
    df = pd.DataFrame(chunks, columns =['fichier', 'chunks'])
    chemin_df = os.path.join(r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2", "table_chunks v2.xlsx")
    df.to_excel(chemin_df)