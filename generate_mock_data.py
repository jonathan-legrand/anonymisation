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
random.seed(1234)

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

def write_analysis(fname, output_path="mock_dataset"):
    """
    Impure function! TODO There's nothing in the analysis files!!!!
    """
    path = f"/tmp/{fname}"
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    
    shutil.make_archive(f"{output_path}/{fname}", "zip", path)
    os.rename(f"{output_path}/{fname}.zip", f"{output_path}/{fname}.analysis")
    shutil.rmtree(path)
    

def generate_id(length):
    digits = (str(random.randint(0, 9)) for _ in range(length))
    return "".join(digits)

def generate_patient_dict(name):
    patient_dict = dict()
    randname_metadata = random_capitalizing(name)
    split_name = randname_metadata.split(" ")
    last_names, first_name = split_name[:-1], split_name[-1]

    for element in last_names:
        if '(' in element:
            joining_char = " "
        else:
            joining_char = ""

    patient_dict["Identifiant patient (NIP)"] = int(generate_id(9))
    patient_dict["Numero clinisight"] = int(generate_id(8))
    patient_dict["NOM"] = joining_char.join(last_names)
    patient_dict["Prénom"] = first_name
    patient_dict["sexe             (1=H, 2=F)"] = random.choice((1, 2))
    return patient_dict


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

        patient_dict = generate_patient_dict(name)
        fake_metadata.append(patient_dict)
        
    fake_metadata = pd.DataFrame(fake_metadata)
    # TODO Add random columns
    #for i in range(10):
    #    dtype = random.choice((int, float, str))
    #    data = random.ra