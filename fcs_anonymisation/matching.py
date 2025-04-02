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
    ratios = []
    for candidate in candidates:
        sim = SM(None, file_id, candidate)
        ratios.append(sim.ratio())
        similarities.append(sim)

    best_match_idx = np.argmax(ratios)
    best_match = similarities[best_match_idx].find_longest_match()

    best_candidate_len = len(candidates[best_match_idx])
    best_match_len = best_match.size

    if best_match.size < len(candidates[best_match_idx]):
        raise ValueError(
            f"""
        Matched :
        {file_id} and
        {candidates[best_match_idx]}
        Best match of length {best_match_len} with a candidate string of length {best_candidate_len}
            """
        )
    return best_match_idx, ratios[best_match_idx]

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
    
    best_match = candidates[best_match_idx]
    print(file_id)
    print(best_match, f" is best match with sim {max_sim}")
    return metadata.iloc[best_match_idx, :], max_sim