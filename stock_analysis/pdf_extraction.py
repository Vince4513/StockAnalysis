import os
import json
import tabula 
import pandas as pd
from datetime import datetime

def df_info(df: pd.DataFrame, message: str = "Data"):
    print(f"---------- {message} ----------")
    print("Shape:", df.shape)
    print(df.info(verbose=False, memory_usage=True))
    print(df)

def extraction_pdf_to_pandas(path: str) -> list[list[pd.DataFrame]]:
    os.chdir(path)
    dataframe_pdfs = []
    for file in os.listdir():
        if file.endswith(".pdf"):
            tables = tabula.read_pdf(file, pages="all")
            print(type(tables))
            dataframe_pdfs.append(tables)
    
    return dataframe_pdfs

def extraction_pdf_to_json(path: str) -> None:
    os.chdir(path)
    for file in os.listdir():
        time = datetime.today()
        time_s = time.strftime("%Y_%m_%d")
        if file.endswith(".pdf"):
            tabula.convert_into(file, f"{time_s}_{file}.json", output_format="json", pages="all")

def read_json(path: str) -> pd.DataFrame:
    os.chdir(path)
    for file in os.listdir():
        if file.endswith(".json"):
            with open(file, "r") as f:
                data = json.load(f)
    
    return data

def extract_from_df(df: pd.DataFrame) -> pd.DataFrame:
    # Assuming df is your DataFrame and strings is a list of strings you want to search for
    lookup_word = ['actifs circulants', 
                   'chiffre d\'affaires', 
                   'passifs circulants',
                   'dettes financières long termes',
                   'dettes financières non courantes',
                   'résultat net',
                   'dividendes',
                   'capitaux propres',
                   'immobilisations incorporelles',
                   'goodwill']

    # Iterate over the rows and print the values
    lines_kept = []
    for index, row in df.iterrows():
        # print(f"Row {index}: {row.values}")

        # Create a boolean mask for each string
        for r in row.values:
            if isinstance(r, str):
                mask = [word in r.lower() for word in lookup_word]
                
                # If a word is found it will add a true value into the mask
                if any(mask):
                    lines_kept.append(index) # Keep only the index from rows containing lookup words 
                    
    # print(lines_kept)
    # Use the boolean mask to filter the DataFrame
    result = df.iloc[lines_kept, :]
    
    return result


def test():
    import pandas as pd

    # Sample DataFrame
    df = pd.DataFrame({'A': [1, float('nan'), 3],
                    'B': [float('nan'), float('nan'), float('nan')],
                    'C': [4, float('nan'), 6]})

    df_filtered = df.dropna(how='all')

    print(df_filtered)

    # words = ['dettes', 'million']
    # rows = ["les dettes se comptent en millions", "la patate", "voiture en panne"]
    # for r in rows:
    #     sel = [w in r for w in words]
    #     print(sel)

def main() -> None:
    current_dir = r"C:\diskD\6 - CODE\StockAnalysis\pdf"

    # extraction_pdf_to_json(current_dir)
    # dfs = read_json(current_dir)
    dfs_pdfs = extraction_pdf_to_pandas(current_dir)
    # df = dfs_pdfs[0][38]
    
    for df in dfs_pdfs[0]:
        # df_info(df, "Extract")
        df_reduced = extract_from_df(df)
        if df_reduced.empty != True:
            df_data = df_reduced.dropna(how='all')
            print("\nDataframe kept:\n", df_data)

if __name__ == "__main__":
    main()
    # test()

    # tables = tabula.read_pdf(file, pages="all")
    # print("\nNombres de Dataframes extraits:", len(tables))
    # dataframes_filtres = []

    # for i in tqdm(range(0, len(tables))):
    #     df = tables[i]
    #     print(f"Dataframe {i}:\n", df, "\n")
        
    #     # Vérifier si au moins une colonne contient le string recherché
    #     if any(df.map(lambda x: isinstance(x, str) and 'actifs courants' in x).any()):
    #         # Ajouter le DataFrame filtré à la liste des DataFrames filtrés
    #         dataframes_filtres.append(df)

    # # Faire quelque chose avec les DataFrames filtrés
    # # Par exemple, afficher le nombre de DataFrames filtrés
    # print("Nombre de DataFrames filtrés :", len(dataframes_filtres))

    # df = tables[38]
    # print(df)
    # if any(df.map(lambda x: isinstance(x, str) and 'actifs courants' in x).any()):
    #         # Ajouter le DataFrame filtré à la liste des DataFrames filtrés
    #         dataframes_filtres.append(df)
    