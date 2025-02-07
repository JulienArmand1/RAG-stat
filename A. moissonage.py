# -*- coding: utf-8 -*-
import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time as time

"""
Objectif : faire le moissonnage web des pdfs
d'analyse de Statistique Canada

1. Lister les liens vers ces pdfs.

2. Télécharger ces pdfs et éviter des doublons.

Je veux garder une trace de l'equivalence pour l'utiliser dans mon retriver.
Je veux le faire pour chaque année pour diviser la tâche.

"""

def telechargement_pdf_annee(argument):
    annee = argument[0]
    nbs_pages = argument[1]

    liste_de_liens = []
    liens = set()
    liste_erreurs = []
    output_dir_gen = r"C:\Users\14388\Desktop\Projet de session\pdf v6"
    debut_url = "https://www150.statcan.gc.ca/n1/fr/type/analyses?pubyear="
    milieu_url = "&count=10&p="
    fin_url = "-analyses/articles_et_rapports&trier=releasedate#articlesetrapports"

    output_dir = os.path.join(output_dir_gen, str(annee))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for page in range(0,nbs_pages+1): # Remetre au bon nombre
        url = debut_url + str(annee) + milieu_url + str(page) +fin_url
        print(url)

        statut = -1
        essai=0
        while statut != 200 and essai<20:
            try:
                essai+=1
                r = requests.get(url, allow_redirects=False, timeout=200)
                statut = r.status_code
                soup = BeautifulSoup(r.text, 'html.parser')
                li_items = soup.find_all('li', class_='ndm-item')

                nbs_liens = 0

                for li in li_items:
                    for link in li.find_all('a', href=True):
                        lien = link.get('href')
                        if 'fra.htm' in lien or 'fra.pdf' in lien or 'fra.html' in lien:
                            nbs_liens += 1
                            lien_pdf = lien.replace(".html", ".pdf").replace(".htm", ".pdf")
                            liens.add(lien_pdf)
                            liste_de_liens.append([nbs_liens,lien_pdf,url])
                            #print(nbs_liens)

            except:
                message = f"Il y a eu une erreur avec {url} à l'essai {essai}"
                liste_erreurs.append(message)
                time.sleep(1)
                print(message)

    print(len(liste_de_liens))
    print(len(liens))


    liens_trouve = pd.DataFrame(liens, columns=['lien trouvé'])
    chemin_liens_trouve = os.path.join(output_dir, str(annee)+"_liens_trouve.xlsx")
    liens_trouve.to_excel(chemin_liens_trouve)


    print("Changement!")
    Equivalence_nom_liens=[]
    nombre_documents=0
    # Téléchargement des liens
    for lien in liens:
        #print(lien)
        response = requests.get(lien)
        if response.status_code == 200:
            nombre_documents += 1
            file_path = os.path.join(output_dir, str(annee)+'_'+str(nombre_documents)+".pdf")
            Equivalence_nom_liens.append([lien,str(annee)+'_'+str(nombre_documents)+".pdf"])
            with open(file_path,'wb') as f:
                f.write(response.content)
        else:
            liste_erreurs.append(f"{lien}")

    sauvegarde_erreur = pd.DataFrame(liste_erreurs, columns=['Erreur_recherche'])
    chemin_sauvegarde_erreur = os.path.join(output_dir, str(annee)+"_Erreur_recherche.xlsx")
    sauvegarde_erreur.to_excel(chemin_sauvegarde_erreur)

    df = pd.DataFrame(Equivalence_nom_liens, columns =['lien', 'nom'])
    chemin_df = os.path.join(output_dir, str(annee)+"_Equivalence_nom_liens.xlsx")
    df.to_excel(chemin_df)

    return liste_de_liens



# Execution

if __name__ == "__main__":
    annees_nbs_pages = [
        [2024, 37],
        [2023, 35],
        [2022, 44],
        [2021, 40],
        [2020, 39],
        [2019, 38],
        [2018, 29],
        [2017, 30],
        [2016, 28],
        [2015, 25],
        [2014, 24],
        [2013, 16],
        [2012, 22],
        [2011, 22],
        [2010, 27],
        [2009, 31],
        [2008, 40],
        [2007, 30],
        [2006, 29],
        [2005, 42],
        [2004, 39],
        [2003, 31],
        [2002, 32],
        [2001, 33],
        [2000, 25],
        [1999, 27],
        [1998, 25],
        [1997, 15],
        [1996, 9],
        [1995, 9],
        [1994, 6],
        [1993, 5],
        [1992, 4],
        [1991, 5],
        [1990, 5],
        [1989, 4],
        [1988, 3],
        [1987, 2],
        [1986, 2],
        [1985, 2],
        [1984, 2],
        [1983, 2],
        [1982, 1],
        [1981, 1],
        [1980, 3],
        [1979, 2],
        [1978, 2],
        [1977, 1],
        [1975, 1]
    ]

    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(telechargement_pdf_annee, annees_nbs_pages))