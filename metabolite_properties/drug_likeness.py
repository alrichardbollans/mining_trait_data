import pandas as pd


def get_bioavailability_rules(in_df: pd.DataFrame, smiles_col:str) -> pd.DataFrame:
    from rdkit.Chem import PandasTools
    from rdkit.Chem.Crippen import MolLogP
    from rdkit.Chem.Descriptors import MolWt
    from rdkit.Chem.Lipinski import NumHAcceptors, NumHDonors, NumRotatableBonds
    from rdkit.Chem.MolSurf import TPSA
    df = in_df[~in_df[smiles_col].isna()].drop_duplicates(subset=smiles_col,keep='first')
    PandasTools.AddMoleculeColumnToFrame(df, smiles_col, 'rdkit_mol')
    df['mw'] = df['rdkit_mol'].apply(lambda x: MolWt(x) if x is not None else None)
    df['logP'] = df['rdkit_mol'].apply(lambda x: MolLogP(x) if x is not None else None)
    df['HBD'] = df['rdkit_mol'].apply(lambda x: NumHDonors(x) if x is not None else None)
    df['HBA'] = df['rdkit_mol'].apply(lambda x: NumHAcceptors(x) if x is not None else None)

    def lipinski_check(row):
        if row['mw'] is not None:
            conditions = [row['mw'] <= 500, row['HBA'] <= 10, row['HBD'] <= 5, row['logP'] <= 5]
            if conditions.count(True) >= 3:
                return 1
            else:
                return 0
        else:
            return None

    df['lipinski_pass'] = df.apply(lambda x: lipinski_check(x), axis=1)

    df['rotatable_bonds'] = df['rdkit_mol'].apply(lambda x: NumRotatableBonds(x) if x is not None else None)
    df['polar_surface_area'] = df['rdkit_mol'].apply(lambda x: TPSA(x) if x is not None else None)

    def veber_check(row):
        if row['mw'] is not None:
            if row['rotatable_bonds'] <= 10 and row['polar_surface_area'] <= 140:
                return 1
            else:
                return 0
        else:
            return None

    df['veber_pass'] = df.apply(lambda x: veber_check(x), axis=1)
    df = df[['veber_pass', 'lipinski_pass', smiles_col]]
    
    return df