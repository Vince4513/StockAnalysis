import os
import tabula 
from tqdm import tqdm

os.chdir(r"C:\diskD\6 - CODE\StockAnalysis\pdf")
for file in os.listdir():
    tables = tabula.read_pdf(file, pages="all")
    print("\nNombres de Dataframes extraits:", len(tables))
    
    for i in tqdm(range(0, len(tables))):
        df = tables[i]
        # print(f"Dataframe {i}:\n", df, "\n")
        
        dataframes_filtres = []
        # Vérifier si au moins une colonne contient le string recherché
        if any(df.map(lambda x: isinstance(x, str) and 'actifs courants' in x).any()):
            # Ajouter le DataFrame filtré à la liste des DataFrames filtrés
            dataframes_filtres.append(df)

    # Faire quelque chose avec les DataFrames filtrés
    # Par exemple, afficher le nombre de DataFrames filtrés
    print("Nombre de DataFrames filtrés :", len(dataframes_filtres))