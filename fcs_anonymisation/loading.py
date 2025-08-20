import xml.etree.ElementTree as ET
from zipfile import ZipFile
import os
import tempfile
from itertools import product
from functools import reduce
from operator import eq

import numpy as np
import pandas as pd
import flowkit as fk
from natsort import natsort_keygen, natsorted

def get_mappings(tree):
    retrieve_list = tree.findall(".//Columns")
    assert len(retrieve_list) == 1, "That's weird"
    cols_element = retrieve_list[0]
    label_mapping = {}
    channel_mapping = {}
    # Hacky stuff for multi datasets files
    for col_element in cols_element:
        if "(2)" not in col_element.attrib["N"]:
            continue
        detector = col_element.find("Detector").text
        label = col_element.find("Description").text
        original_name = col_element.find("OriginalName").text
        channel_mapping[detector] = original_name
        label_mapping[original_name] = label
    return label_mapping, channel_mapping

class SampleCorrectChannelIndices(fk.Sample):
    def __init__(self, *args, **kwargs):
        if "compensation" in kwargs.keys():
            comp = kwargs.pop("compensation")
        else:
            comp = None

        super().__init__(*args, **kwargs)
        
        # Correct channel idx issues before compensation,
        # because flowkit automatic process does not work
        # with our data
        fluoro_indices = []
        scatter_indices = []
        null_channels = []
        for idx, label in enumerate(self.pnn_labels):
            if "FS" in label or "SS" in label:
                scatter_indices.append(idx)
            elif "FL" in label:
                fluoro_indices.append(idx)
            else:
                null_channels.append(label)

        labels = np.array(self.pnn_labels)
        print("Automatically assigned fluo/scatter/null idx") 
        print("fluo : ", labels[fluoro_indices]) 
        print("scatter : ", labels[scatter_indices]) 
        print("null : ", null_channels) 

        self.fluoro_indices = fluoro_indices
        self.scatter_indices = scatter_indices
        self.null_channels = null_channels

        self.compensation = comp
        self.metadata["spill"] = comp
        self.apply_compensation(comp)

class XMLCompensation:
    def __init__(self, xml_path):
        self._load_compensation(xml_path)

    def _load_compensation(self, xml_path: str) -> fk.Matrix:
        """
        Read manual compensation matrix from xml files.
        Use a lot of natsorting so that FL1 < FL2 < FL10 and not FL1 < FL10 < FL2
        Not natsorting leads to funny compensation bugs.

        Args:
            xml_path (str): path to the xml file from analysis archive,
            which contains the manual compensation.

        Returns:
            fk.Matrix: Flowkit compensation matrix, with properly sorted channels
        """
        tree = ET.parse(xml_path)
        retrieve_list = tree.findall(".//Compensation")
        assert len(retrieve_list) == 1, "That's weird"
        compensation_element = retrieve_list[0]

        generator = (child.attrib for child in compensation_element.find("S"))
        
        
        self.compensation_df = pd.DataFrame(generator).sort_values(by="S", key=natsort_keygen())
        self.tree = tree

    @property
    def compensation_matrix(self) -> fk.Matrix:
        compensation_df = self.compensation_df.copy()
        label_mapping, channel_mapping = get_mappings(self.tree)

        compensation_df["S"] = compensation_df["S"].apply(lambda x: channel_mapping[x])
        compensation_df["C"] = compensation_df["C"].apply(lambda x: channel_mapping[x])

        p = compensation_df.pivot(index="S", columns="C", values="V").astype(float)
        p = p.sort_index(key=natsort_keygen()).reindex(natsorted(p.columns), axis=1)
        p.fillna(0, inplace=True)
        np.fill_diagonal(p.values, 1)
    
        sources = p.index.to_list()
        fluorochromes = [label_mapping[el] for el in sources]
    
        matrix = fk.Matrix(p.values, sources, fluorochromes)

        return matrix
    
    @property
    def compensation_spill_string(self) -> str:
        df = self.compensation_df
        sensors = df.S.unique()

        n_sensors = len(sensors)
        spill_string = f"{len(sensors)}"
        for sensor in sensors:
            spill_string += f",{sensor}"

        for pair in product(sensors, sensors):
            if reduce(eq, pair):
                spill_string += ",1"
                continue

            msk = (df.S == pair[0]) & (df.C == pair[1])
            n_matches = msk.sum()
            if n_matches == 1:
                spill_value = df.loc[msk, "V"].values[0]
                spill_string += f",{spill_value}"
            elif n_matches == 0:
                spill_string += f",0"
            else:
                raise ValueError(f"Too many matches, something is wrong")

        assert len(spill_string.split(",")) == (n_sensors ** 2 + n_sensors + 1)
        return spill_string


from rpy2.robjects import r
from rpy2.robjects.methods import RS4


# Load the R file
r['source']('R_functions/sample_anonymisation.R')

def read_analysis(fpath):
    """
    Extract analysis files using R function, read compensation
    """
    R_output = r['anonymize_sample'](str(fpath)) # That could be not cross platform
    temp_xml_fname = list(R_output[1])[0]
    sample = R_output[0]
    compensation = XMLCompensation(temp_xml_fname)
    os.remove(temp_xml_fname)

    return sample, compensation
    
