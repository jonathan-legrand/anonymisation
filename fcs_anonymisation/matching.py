# TODO Match second convention
from difflib import SequenceMatcher as SM
import matplotlib.pyplot as plt
import numpy as np

def is_junk(character):
    if character in ("(", ")", "_"):
        return True
    return False

def best_matching_row(file_id, metadata):
    """
    This could probably be better optimized, because for now we
    are using the whole fname. We know that the interesting
    stuff for matching happens at the beginning
    """
    file_id = file_id.lower()
    concatnames = metadata["NOM"] + " " + metadata["Prénom"]
    candidates = concatnames.apply(lambda string: string.lower()).to_list()

    similarities = []
    for candidate in candidates:
        sim = SM(is_junk, file_id, candidate)
        similarities.append(sim.ratio())

    best_match_idx = np.argmax(similarities)
    max_sim = similarities[best_match_idx]
    if max_sim < 0.3: # This threshold is somewhat arbitrary
        raise ValueError(f"Max similarity = {max_sim} < 0.3")

    best_match = candidates[best_match_idx]
    print(file_id)
    print(best_match, " is best match", end="\n\n")
    return best_match, similarities[best_match_idx]