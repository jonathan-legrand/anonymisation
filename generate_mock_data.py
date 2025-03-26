"""
Create fake data
We need to : 
- generate stupid names
- compress fcs and xml to zip
- rename zip to .analysis
- Corresponding entries in metadata?

"""
# %%
from pathlib import Path
import shutil
import os
import pandas as pd
import random
from fcs_anonymisation import get_config

config = get_config()
datapath = Path(config["DATAPATH"])
metadata = pd.read_excel(datapath / "metadata.xlsx")

fcs_path = datapath / "0001.fcs"
xml_path = datapath / "000003.xml"

def capitalize_lastname(string):
    split = string.split(" ")
    if len(split) == 2:
        last, first = string.split(" ")
        return last.upper() + " " + first
    return string

def random_capitalizing(string):
    """
    Lower, upper whole string or first letter
    """
    choices = (
        capitalize_lastname,
        lambda x: x.upper(),
        lambda x: x.lower(),
        lambda x: x
    )
    func = random.choice(
        choices
    )
    return func(string)

if __name__ == "__main__":
    with open("fake_names.txt", "r") as f:
        names = f.read().splitlines()
    for name in names:
        source = random_capitalizing(
            random.choice(("Moelle", "Sang"))
        )
        randname = random_capitalizing(name)
        fname = f"{randname} {source} blabla blabla-bla_bla"
        path = f"/tmp/{fname}"
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
    
        shutil.make_archive(f"mock_dataset/{fname}", "zip", path)
        os.rename(f"mock_dataset/{fname}.zip", f"mock_dataset/{fname}.analysis")
