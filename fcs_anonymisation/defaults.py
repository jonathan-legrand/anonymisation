COL_WHITE_LIST = [
    "Identifiant patient (NIP)",
    "Numero clinisight",
    "sexe             (1=H, 2=F)",
    "FLT3",
    "NPM"
]

# Optional description of columns
# for the patients.json file
COLS_DESCRIPTION = {
    "Identifiant patient (NIP)": {
        "Description": "Patients ID",
    },
    "sexe             (1=H, 2=F)": {
        "Description": "Patient's sex",
        "Levels": {
            "1": "Man",
            "2": "Woman"
        }
    },
    "FLT3": {
        "Description": "FLT3 mutation status",
        "Levels": {
            "WT": "Not mutated",
            "ITD": "Internal Tandem Duplication",
            "TKD": "Tyrosine Kinase Domain",
            "NF": "Non Fait, undetermined"
        }
    },
    "NPM": {
        "Description": "NPM mutation status"
    }
}

TAGS_WHITE_LIST = []