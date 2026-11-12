# Independent Enzyme Digestion Pipeline

A Python tool to simulate independent in vitro enzymatic digestion (Pepsin, Trypsin, Chymotrypsin, Elastase, and Carboxypeptidase) in parallel on designed peptide sequences, aggregate unique fragments, and export structured multi-sheet Excel reports.

## Features

- Independent multi-enzyme cleavage simulation per peptide.
- Endopeptidase and exopeptidase (Carboxypeptidase) handling.
- Aggregated unique fragment extraction (length >= 2) across all enzymes.
- Clean Excel export with separate overview and unique fragment sheets.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run with default settings:
```bash
python enzyme_digestion.py
```

Or specify a custom input file and output name:
```bash
python enzyme_digestion.py /path/to/PEPTIDE_MUTATION_docking.xlsx -o custom_enzyme_results.xlsx
```
