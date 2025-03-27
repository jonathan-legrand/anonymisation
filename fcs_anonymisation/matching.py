# TODO Match second convention
from difflib import SequenceMatcher as SM
import matplotlib.pyplot as plt
import numpy as np

def is_junk(character):
    if character in ("(", ")", "_", " ", "BDX-"):
        return True
    return False

def best_matching_row(file_id, metadata):
    """
    Search for similarity with ID or name (depends if it starts with BDX) 
    This could probably be better optimized, because for now we
    are using the whole fname. We know that the interesting
    stuff for matching happens at the beginning
    """
    file_id = file_id.lower()
    concatnames = metadata["NOM"] + " " + metadata["Prénom"]
    patient_ids = metadata["ID"].apply(lambda string: string.lower())
    names = concatnames.apply(lambda string: string.lower()).to_list()

    if file_id[:3] == "bdx":
        candidates = patient_ids
    else:
        candidates = names
        
    similarities = []
    for candidate in candidates:
        sim = SM(is_junk, file_id, candidate)
        similarities.append(sim.ratio())

    best_match_idx = np.argmax(similarities)
    max_sim = similarities[best_match_idx]

    best_match = candidates[best_match_idx]
    print(file_id)
    print(best_match, " is best match")
    return metadata.iloc[best_match_idx, :], max_sim