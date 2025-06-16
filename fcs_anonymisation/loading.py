import xml.etree.ElementTree as ET
from zipfile import ZipFile
import re
import os
import tempfile
from itertools import product
from functools import reduce
from operator import eq

import numpy as np
import pandas as pd
import flowkit as fk
from flowutils.compensate import parse_compensation_matrix
from flowio import read_multiple_data_sets
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

class SampleManualCompensation(SampleCorrectChannelIndices):
    def __init__(self, *args, xml_path, **kwargs):
        super().__init__(*args, **kwargs)
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



fcs_pattern = re.compile(r".*\.fcs$")
xml_pattern = re.compile(r".*\.xml$")

def read_analysis(fpath):
    """
    Extract analysis files, read and apply compensation, return fcs.
    At this stage, the FCS isn't anonymous yet.
    """
    with ZipFile(fpath, "r") as analysis:
        fnames = analysis.namelist()
        fcs_files = tuple(filter(fcs_pattern.match, fnames))
        xml_files = tuple(filter(xml_pattern.match, fnames))
        assert len(fcs_files) == 1
        assert len(xml_files) == 1

        # Extract the FCS file to a temporary file and read datasets from it
        # because read_multiple_datasets is broken with file streams
        with tempfile.NamedTemporaryFile(delete=False) as tmp_fcs:
            tmp_fcs.write(analysis.read(fcs_files[0]))
            tmp_fcs_path = tmp_fcs.name

        # Read the FCS file using the file path
        # Sometimes there are several datasets per 
        # fcs file, we are only interested in first one
        samples = read_multiple_data_sets(tmp_fcs_path)
        with analysis.open(xml_files[0]) as xml_handle:
            sample = SampleManualCompensation(
                samples[-1], xml_path=xml_handle
            )

        os.remove(tmp_fcs_path)

    return sample
    
