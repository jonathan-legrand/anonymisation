# %%
docstring = """
We want to convert a directory of sensitive analysis file and convert
them to usable, anonymous fcs data, with the proper compensation matrices.
"""
import argparse
import os
import json
from pathlib import Path

from matplotlib import pyplot as plt
import pandas as pd
import flowkit as fk
import seaborn as sns

from fcs_anonymisation.loading import read_analysis
from fcs_anonymisation.matching import best_matching_row, get_specimen
from fcs_anonymisation.defaults import (
    COLS_DESCRIPTION,
    COL_WHITE_LIST,
    TAGS_WHITE_LIST
)


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
    #parser = mock_parser()
    parser = init_argparse()
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
    
    os.makedirs(
        output_path / "compensation_matrices",
        exist_ok=True
    )
    os.makedirs(
        output_path / "samples",
        exist_ok=True
    )

    anonymous_metadata = []
    for fpath in input_path.iterdir():
        sample = read_analysis(fpath)
        matching_row, _ = best_matching_row(fpath.name, metadata)
        specimen = get_specimen(fpath.name)
        new_name = matching_row[new_name_col]

        export_name = f"id-{new_name}_specimen-{specimen}"

        print(new_name, end="\n\n")

        sample_df = sample.as_dataframe(
            source="raw",
            subsample=False,
            col_multi_index=True,
        )
        sample_compensation = sample.compensation.as_dataframe(fluoro_labels=True)

        anonymous_sample = fk.Sample(
            sample_df,
            sample_id=new_name,
            compensation=sample.compensation
        )
        # TODO Add sample origin, blood or marrow
        anonymous_sample.export(
            filename=export_name + ".fcs",
            source="raw",
            include_metadata=False,
            directory=output_path / "samples"
        )
        sample_compensation.to_csv(
            output_path / "compensation_matrices" / (export_name + ".csv")
        )

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
