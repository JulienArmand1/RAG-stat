# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 16:42:38 2024

@author: 14388
"""
import pandas as pd
import numpy as np
from statsmodels.stats.anova import AnovaRM
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

df_long_100 = df_long_100[df_long_100['modalite'].str.contains("llama") == False]
df_long_500 = df_long_500[df_long_500['modalite'].str.contains("llama") == False]

df_long_100["nbs_chunks"] = np.tile(np.repeat(np.arange(10), 100), 4)
df_long_500["nbs_chunks"] = np.tile(np.repeat(np.arange(10), 100), 4)

df_long_100['modele'] = np.where(df_long_100['modalite'].str.contains("gemini"),1,0)
df_long_500['modele'] = np.where(df_long_500['modalite'].str.contains("gemini"),1,0)

df_long_100['longueur'] = np.where(df_long_100['modalite'].str.contains("court"),1,0)
df_long_500['longueur'] = np.where(df_long_500['modalite'].str.contains("court"),1,0)

df_long = pd.concat([df_long_100,df_long_500])

aov = AnovaRM(df_long, depvar='score', subject='questions', within=["nbs_chunks","modele","taille","longueur"]).fit()
print(aov)