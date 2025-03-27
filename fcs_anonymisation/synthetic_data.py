
import os
from pathlib import Path
import random
import shutil


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

def create_analysis(
        fname,
        fcs_path,
        xml_path,
        output_path="mock_dataset"
    ):
    """
    Impure function!
    """
    temp_path = Path("/tmp") / fname
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    os.mkdir(temp_path)
    shutil.copyfile(fcs_path, temp_path / f"uninformative_name.fcs")
    shutil.copyfile(xml_path, temp_path / f"uninformative_name.xml")
    
    shutil.make_archive(f"{output_path}/{fname}", "zip", temp_path)
    os.rename(f"{output_path}/{fname}.zip", f"{output_path}/{fname}.analysis")
    shutil.rmtree(temp_path)
    

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

