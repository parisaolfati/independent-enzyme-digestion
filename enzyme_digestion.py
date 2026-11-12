# -*- coding: utf-8 -*-
"""Independent multi-enzyme digestion pipeline for designed peptides."""

import argparse
from pathlib import Path
import re
import pandas as pd


def digest_sequence(sequence, enzyme_pattern, is_exopeptidase=False):
    """Digest peptide sequence based on specified enzyme pattern."""
    if pd.isna(sequence) or sequence == "":
        return ""

    sequence = str(sequence).strip()

    if not is_exopeptidase:
        fragments = re.sub(f'({enzyme_pattern})', r'\1 ', sequence).strip().split()
        return "-".join(fragments)
    else:
        fragments = []
        peptide = sequence

        while len(peptide) > 1 and peptide[-1] in enzyme_pattern:
            fragments.insert(0, peptide[-1])
            peptide = peptide[:-1]

        if peptide:
            fragments.insert(0, peptide)

        return "-".join(fragments)


def extract_combined_unique_fragments(df, enzyme_cols, min_length=2):
    """Extract and aggregate unique fragments across all enzymes with length >= min_length."""
    all_fragments = []
    
    for col in enzyme_cols:
        for digested_str in df[col].dropna():
            parts = str(digested_str).split("-")
            for p in parts:
                clean_p = p.strip()
                if len(clean_p) >= min_length:
                    all_fragments.append(clean_p)
    
    unique_list = pd.Series(all_fragments).drop_duplicates().tolist()
    return pd.DataFrame({'Unique_Fragments': unique_list})


def run_digestion(file_path: Path, output_filename: str):
    """Run individual enzyme digestion per peptide sequence."""
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        df = pd.read_excel(file_path)
        df.columns = df.columns.astype(str).str.strip()

        if 'Designed peptides' not in df.columns:
            raise KeyError("Column 'Designed peptides' not found in input file.")

        patterns = {
            'Pepsin': '[DEFYW]',
            'Trypsin': '[RK]',
            'Chymotrypsin': '[FYWLM]',
            'Elastase': '[GA]',
            'Carboxypeptidase': {'F', 'Y', 'W', 'L', 'I', 'V', 'R', 'K'}
        }

        enzymes = ['Pepsin', 'Trypsin', 'Chymotrypsin', 'Elastase', 'Carboxypeptidase']
        enzyme_cols = []

        # Process digestion per enzyme independently
        for enz in enzymes:
            is_exo = (enz == 'Carboxypeptidase')
            pattern = patterns[enz]
            col_name = f'After_{enz}'
            enzyme_cols.append(col_name)
            
            df[col_name] = df['Designed peptides'].apply(
                lambda seq: digest_sequence(seq, pattern, is_exopeptidase=is_exo)
            )

        # Extract combined unique fragments
        df_combined_unique = extract_combined_unique_fragments(df, enzyme_cols, min_length=2)

        output_path = file_path.parent / output_filename

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='All_Digestion_Results', index=False)
            df_combined_unique.to_excel(writer, sheet_name='All_Enzymes_Unique_>=2aa', index=False)

        print(f"Digestion process completed successfully.\nOutput saved to: {output_path.resolve()}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run independent multi-enzyme digestion simulations on designed peptides.")
    parser.add_argument(
        "input_file",
        nargs="?",
        default="PEPTIDE MUTATION docking.xlsx",
        type=Path,
        help="Path to the input Excel file containing 'Designed peptides' (default: PEPTIDE MUTATION docking.xlsx)."
    )
    parser.add_argument(
        "-o", "--output",
        default="enzyme_results_per_peptide.xlsx",
        help="Output Excel filename (default: enzyme_results_per_peptide.xlsx)."
    )
    args = parser.parse_args()
    
    run_digestion(args.input_file, args.output)
