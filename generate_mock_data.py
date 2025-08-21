"""
Create fake data
We need to : 
- generate stupid names
- compress fcs and xml to zip
- rename zip to .analysis
- Corresponding entries in metadata?

"""
from pathlib import Path
import pandas as pd
import numpy as np
import random
from fcs_anonymisation import get_config
from fcs_anonymisation.synthetic_data import (
    create_analysis,
    generate_patient_dict,
    random_capitalizing,
    generate_id,
    generate_string
)

config = get_config()
datapath = Path(config["DATAPATH"])
metadata = pd.read_excel(datapath / "metadata.xlsx")

fcs_path = datapath / "000010.fcs"
xml_path = datapath / "000011.xml"
random.seed(1234)
rng = np.random.default_rng(seed=1234)
N_MOCK_COLUMNS = 10

def name_with_names(name, source, ID):
    return f"{name} {source} bla bla-bla_bla {generate_id(4)}"

def name_with_problematic_id(name, source, ID):
    return f"BDX-{ID} {source} bla bla-bla_bla {generate_id(4)}"

naming_conventions = (
    name_with_names, name_with_problematic_id
)

if __name__ == "__main__":
    with open("fake_names.txt", "r") as f:
        names = f.read().splitlines()
    fake_metadata = []
    for name in names:
        
        source = random_capitalizing(
            np.random.choice(
                ("Moelle", "Sang", "Sng", "Moele"),
                p=(0.4, 0.4, 0.1, 0.1) # We want to be robust against bad spelling
            )
        )
        randname_analysis = random_capitalizing(name)
        ID = generate_string(5) + generate_id(8)

        naming_func = random.choice(naming_conventions)
        fname = naming_func(name, source, ID)

        create_analysis(fname, fcs_path, xml_path)

        patient_dict = generate_patient_dict(name)
        patient_dict["ID"] = ID
        
        # Just for fun, assume that sometimes a file
        # does not correspond to an entry in metadata.
        skip_metadata = np.random.choice(
            (True, False), p=(0.1, 0.9)
        )
        if skip_metadata:
            print(f"Exluded {patient_dict}")
            continue
        fake_metadata.append(patient_dict)
        
    fake_metadata = pd.DataFrame(fake_metadata)

    # Add random columns and export
    for i in range(N_MOCK_COLUMNS):
        dtype = random.choice((int, float, str))
        data = pd.Series(rng.random(size=len(fake_metadata))) * 10
        data = data.astype(dtype)
        fake_metadata[f"mock_col_{i}"] = data

    fake_metadata.to_excel("mock_metadata.xlsx", index=0)