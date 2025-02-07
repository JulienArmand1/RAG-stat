# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 22:17:29 2024

@author: 14388
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 16:42:38 2024

@author: 14388
"""
import pandas as pd
import numpy as np
from statsmodels.stats.anova import AnovaRM
import seaborn as sns
import os

# Lecture des données
analyse_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2\M. Analyse\Analyse version finale"
data100 = pd.read_excel(os.path.join(analyse_dir, 'analyse100_score_test.xlsx'))
data500 = pd.read_excel(os.path.join(analyse_dir, 'analyse500_score_test.xlsx'))

# Préparation des jeux de données

df_long_100 = data100.melt(value_name='score', var_name='modalite')
df_long_500 = data500.melt(value_name='score', var_name='modalite')

df_long_100['questions'] = np.tile(np.arange(1, 101), len(df_long_100) // 100)
df_long_500['questions'] = np.tile(np.arange(1, 101), len(df_long_500) // 100)

df_long_100['taille'] = 1
df_long_500['taille'] = 0


df_long_100["nbs_chunks"] = np.concatenate([
    np.repeat(2, 100),
    np.repeat(8, 100),
    np.repeat(2, 100),
    np.repeat(8, 100),
    np.tile(np.repeat([0,1,2,4,8,16,32,64,126,256], 100), 4)
])

# Pour df_long_500
df_long_500["nbs_chunks"] = np.concatenate([
    np.repeat(2, 100),
    np.repeat(8, 100),
    np.repeat(2, 100),
    np.repeat(8, 100),
    np.tile(np.repeat([0,1,2,4,8,16,32,64,126,256], 100), 4)
])

df_long_100['modele'] = np.where(df_long_100['modalite'].str.contains("gemini"),"Gemini-1.5-flash","GPT-4o")
df_long_500['modele'] = np.where(df_long_500['modalite'].str.contains("gemini"),"Gemini","GPT-4o")
df_long_100['modele'] = np.where(df_long_100.index.isin(range(0, 400)),"Llama 3.2 3b",df_long_100['modele'])
df_long_500['modele'] = np.where(df_long_500.index.isin(range(0, 400)),"Llama 3.2 3b",df_long_500['modele'])

df_long_100['longueur'] = np.where(df_long_100['modalite'].str.contains("court"),"court","long")
df_long_500['longueur'] = np.where(df_long_500['modalite'].str.contains("court"),"court","long")

df_long_100_v2 = df_long_100[df_long_100['modalite'].str.contains("llama") == False]
df_long_500_v2 = df_long_500[df_long_500['modalite'].str.contains("llama") == False]

df_long = pd.concat([df_long_100_v2,df_long_500_v2])


# Graphique
sns.set_theme(style="whitegrid")
sns.set_context("talk", font_scale=1)

g = sns.catplot(
    data = df_long_500, x="nbs_chunks", y="score", hue="modele", col="longueur",
    capsize=.2, palette="YlGnBu_d", errorbar="se",
    kind="point", height=6, aspect=.75,
)
g.despine(left=True)