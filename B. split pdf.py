import os
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd

def split_pdf_by_range(name_pdf,input_pdf, output_folder):
    """
    Prend un pdf et le sépare par groupe de 5 pages
    """
    liste_nom = [] # Pour le fichier d'équivalence avec les documents séparés
    nbs_pages_split = 5
    with open(input_pdf, 'rb') as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)

        count_step = 1
        for start in range(0, num_pages, nbs_pages_split):
            writer = PdfWriter()
            end = min(start + nbs_pages_split, num_pages)
            for page_num in range(start, end):
                writer.add_page(reader.pages[page_num])

            nom_doc = f"{name_pdf}_{count_step}.pdf"
            output_filename = os.path.join(
                output_folder,
                nom_doc
            )
            count_step+=1

            with open(output_filename, 'wb') as output_pdf:
                writer.write(output_pdf)
            liste_nom.append([name_pdf,nom_doc])

    return liste_nom

if __name__ == "__main__":

    input_dir = r"C:\Users\14388\Desktop\Projet de session\pdf v6"
    output_dir = r"C:\Users\14388\Desktop\Projet de session\pdf v6 mod"
    nouvelle_equivalence = []

    for annee in os.listdir(input_dir):
        print(annee)
        dir_pdf_annee = os.path.join(input_dir, annee)
        for doc in os.listdir(dir_pdf_annee):
            path = os.path.join(dir_pdf_annee, doc)
            if ".pdf" in doc:
                name_pdf = doc.replace('.pdf', '')
                liste_nom = split_pdf_by_range(name_pdf, path, output_dir)
                nouvelle_equivalence = nouvelle_equivalence+liste_nom

    colonne_name = ['nom_avant_separation', 'nom_après_separation']
    df = pd.DataFrame(nouvelle_equivalence, columns = colonne_name)
    chemin_df = os.path.join(output_dir, "Nouvelle_equivalence.xlsx")
    df.to_excel(chemin_df)

    for annee in range(1975,2025):
        path = os.path.join(input_dir, str(annee))
        if os.path.isdir(path) :
            file_path = os.path.join(path, str(annee)+"_Equivalence_nom_liens.xlsx")
            dff = pd.read_excel(file_path)
            if annee == 1975:
                df1 = dff
            else:
                df1 = pd.concat([df1,dff],ignore_index=True, axis=0)
    df1.to_excel(chemin_df)
    df1['nom_avant_separation'] = df1['nom'].str.replace('.pdf', '')

    df_left = pd.merge(df, df1, on='nom_avant_separation', how='left')
    df_left.drop(['nom', 'Unnamed: 0'], axis='columns', inplace=True)

    chemin_df = os.path.join(r"C:\Users\14388\Desktop\Projet de session", "Equivalence_complete.xlsx")
    df_left.to_excel(chemin_df)