# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 16:12:56 2024

@author: 14388
"""
import os
import pandas as pd
import numpy as np

if __name__ == "__main__":

    # Importation des embeddings
    input_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2\H2. embeddings"
    for name in os.listdir(input_dir):
        print(name)
        path = os.path.join(input_dir, name)
        dff = pd.read_csv(path, header=None)
        if name == "1975.csv":
            df1 = dff
        else:
            df1 = pd.concat([df1,dff],ignore_index=True, axis=0)
    arr = df1.to_numpy()

    # Exportation des vecteurs
    output_dir = r"C:\Users\14388\Desktop\Projet de session\Projet final version clean v2"
    path_data2 = os.path.join(output_dir, "L2. Embeddings.csv")
    np.savetxt(path_data2, arr, delimiter=',',fmt='%.18f')