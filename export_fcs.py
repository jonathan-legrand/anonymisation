# %%
docstring = """
We want to convert a directory of sensitive analysis file and convert
them to usable, anonymous fcs data, with the proper compensation matrix.
"""
import argparse
import os
from pathlib import Path

import pandas as pd

from fcs_anonymisation.loading import read_analysis
from fcs_anonymisation.matching import best_matching_row

COL_WHITE_LIST = [
    "Identifiant patient (NIP)",
    "Numero clinisight",
    "sexe             (1=H, 2=F)",
    "mock_col_2"
]
TAGS_WHITE_LIST = []

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=docstring
    )
    parser.add_argument(
        "--input_directory",
        help="Directory containing the raw analysis files",
        default="mock_dataset" # TODO For tests only
    )
    parser.add_argument(
        "--metadata",
        help="csv or xlsx files containing patients information",
        default="mock_metadata.csv"
    )
    parser.add_argument(
        "--output_dir",
        help="Path to output dir, default is anonymous_fcs in current directory",
        type=str,
        default="anonymous_fcs"
    )
    parser.add_argument(
        "--rename_with_col",
        help="Path to output dir, default is anonymous_fcs in current directory",
        type=str,
        default="Numero clinisight"
    )
    return parser

def mock_parser():
    class Parser:
        def parse_args(self):
            args = {
                "input_directory": "mock_dataset",
                "metadata": "mock_metadata.xlsx",
                "output_dir": "mock_output",
                "rename_with_col": "Numero clinisight",
            }
            return args
    return Parser()


if __name__ == "__main__":
    parser = mock_parser()
    args = parser.parse_args()
    print(args)

    input_path = Path(args["input_directory"])
    new_name_col = args["rename_with_col"]
    
    metadata = pd.read_excel(
        args["metadata"]
    )

    for fpath in input_path.iterdir():
        sample = read_analysis(fpath)
        matching_row, _ = best_matching_row(fpath.name, metadata)
        new_name = matching_row[new_name_col]
        print(new_name, end="\n\n")

    os.makedirs(
        args["output_dir"],
        exist_ok=True
    )

# %%
