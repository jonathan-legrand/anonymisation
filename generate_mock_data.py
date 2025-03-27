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
    create_analysis, generate_patient_dict, random_capitalizing
)

config = get_config()
datapath = Path(config["DATAPATH"])
metadata = pd.read_excel(datapath / "metadata.xlsx")

fcs_path = datapath / "0001.fcs"
xml_path = datapath / "000003.xml"
random.seed(1234)
rng = np.random.default_rng(seed=1234)
N_MOCK_COLUMNS = 10

if __name__ == "__main__":
    with open("fake_names.txt", "r") as f:
        names = f.read().splitlines()
    fake_metadata = []
    for name in names:
        
        source = random_capitalizing(
            random.choice(("Moelle", "Sang"))
        )
        randname_analysis = random_capitalizing(name)
        fname = f"{randname_analysis} {source} blabla blabla-bla_bla"
        create_analysis(fname, fcs_path, xml_path)

        patient_dict = generate_patient_dict(name)
        fake_metadata.append(patient_dict)
        
    fake_metadata = pd.DataFrame(fake_metadata)

    # Add random columns and export
    for i in range(N_MOCK_COLUMNS):
        dtype = random.choice((int, float, str))
        data = pd.Series(rng.random(size=len(fake_metadata))) * 10
        data = data.astype(dtype)
        fake_metadata[f"mock_col_{i}"] = data

    fake_metadata.to_csv("mock_metadata.csv")