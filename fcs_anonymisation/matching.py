# TODO Match second convention
from difflib import SequenceMatcher as SM
import matplotlib.pyplot as plt
import numpy as np
import math

def is_junk(character):
    if character in ("(", ")", "_", " ", "BDX-"):
        return True
    return False


specimen_french = ["moelle", "sang"]
specimen_english = ["marrow", "blood"]
specimen_translation = dict(zip(specimen_french, specimen_english))

def get_specimen(file_id):
    """
    Here we want an exact match, there aren't so many
    ways to write sang and moelle.
    """
    file_id = file_id.lower()
    specimen = "unknown"
    for word in file_id.split(" "):
        for candidate in specimen_french:
            if word == candidate:
                specimen = specimen_translation[word]
    return specimen

def matching(file_id, candidates):
    """
    Match sequences with difflib. We enforce that 
    the candidate key is fully matched, otherwise
    raise a value error.
    """
    similarities = []
    for idx, candidate in enumerate(candidates):
        sm = SM(None, file_id, candidate)
        similarities.append(
            (idx, sm, candidate)
        )

    best_idx, best_sim, best_candidate = max(similarities, key=lambda x: x[1].ratio())
    best_match = best_sim.find_longest_match()

    if best_match.size != len(best_candidate):
        raise ValueError(
            f"""
        Could not match :
        {file_id}
        {best_candidate} is best candidate
        Best match of length {len(best_match)} with a candidate string of length {len(best_candidate)}
            """
        )
    return best_idx, best_sim.ratio()

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
    best_match_idx, max_sim = matching(file_id, candidates)
    
    best_candidate = candidates[best_match_idx]
    print(file_id)
    print(best_candidate, f" is best candidate with sim {max_sim}")
    return metadata.iloc[best_match_idx, :], max_sim