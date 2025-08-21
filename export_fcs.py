# %%
docstring = """
We want to convert a directory of sensitive analysis file and convert
them to usable, anonymous fcs data, with the proper compensation matrices.
"""
import warnings
import argparse
import os
import json
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from fcs_anonymisation.loading import read_analysis, SampleCorrectChannelIndices
from fcs_anonymisation.matching import best_matching_row, get_specimen
from fcs_anonymisation.defaults import (
    COLS_DESCRIPTION,
    COL_WHITE_LIST,
)

from rpy2.robjects import r

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=docstring
    )
    parser.add_argument(
        "--input_dir",
        help="Directory containing the raw analysis files",
    )
    parser.add_argument(
        "--metadata",
        help="csv or xlsx files containing patients information",
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
        default="Identifiant patient (NIP)"
    )
    parser.add_argument(
        "--colspecs",
        help="Path to dir containing cols white list and description",
        type=str,
        default=None
    )
    return parser

def mock_parser():
    class Parser:
        def parse_args(self):
            args = {
                "input_dir": "mock_dataset",
                "metadata": "mock_metadata.xlsx",
                "output_dir": "mock_output",
                "rename_with_col": "Identifiant patient (NIP)",
                "colspecs": "colspecs/mock_data",
            }
            return argparse.Namespace(**args)
    return Parser()


def load_col_specs(args):
    colspecs = args["colspecs"]
    if colspecs is None:
        return COL_WHITE_LIST, COLS_DESCRIPTION
    else:
        colspecs = Path(colspecs)
        with open(colspecs / "white_list.json") as stream:
            col_white_list = json.load(stream)
        with open(colspecs / "cols_description.json") as stream:
            cols_description = json.load(stream)
        return col_white_list, cols_description
        

if __name__ == "__main__":
    parser = init_argparse()
    #parser = mock_parser()
    args = vars(parser.parse_args())
    print(args)

    print(args["input_dir"])
    input_path = Path(args["input_dir"])
    output_path = Path(args["output_dir"])
    new_name_col = args["rename_with_col"]
    col_white_list, cols_description = load_col_specs(args)
    
    metadata = pd.read_excel(
        args["metadata"]
    )

    os.mkdir(output_path)
    
    anonymous_metadata = []
    for fpath in input_path.iterdir():
        r_sample, compensation = read_analysis(fpath)
        try:
            matching_row, _ = best_matching_row(fpath.name, metadata)
        except ValueError as err:
            print(err)
            print(f"No good enough matching row found for {fpath}, skipping")
            continue


        specimen = get_specimen(fpath.name)
        new_name = matching_row[new_name_col]

        export_name = f"sub-{new_name}_specimen-{specimen}"
        print("export to", export_name, end="\n\n")

        os.mkdir(output_path / export_name)
        
        from rpy2.robjects.vectors import StrVector
        
        # Export sample using R flowCore
        fcs_output_name = str(output_path / export_name / f"{export_name}_sample.fcs")
        r("library(flowCore)")
        r.assign("anonymous_sample", r_sample)
        r(f"identifier(anonymous_sample) <- '{export_name}'")

        r(f"write.FCS(anonymous_sample, filename = '{fcs_output_name}')")

        # Also export compensation by itself to be explicit
        compensation.mat_from_spill.as_dataframe(fluoro_labels=False).to_csv(
            output_path / export_name / f"{export_name}_compensation.csv"
        )

        # Store subject's anonymous metadata
        anonymous_metadata.append(
            matching_row[col_white_list]
        )
    anonymous_metadata = pd.DataFrame(anonymous_metadata)
    anonymous_metadata.to_csv(
        output_path / "patients.tsv", sep="\t"
    )
    with open(output_path / "patients.json", "w") as stream:
        json.dump(cols_description, stream)


# %%
