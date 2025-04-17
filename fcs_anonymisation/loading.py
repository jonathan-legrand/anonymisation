import xml.etree.ElementTree as ET
from zipfile import ZipFile
import re
import os
import tempfile

import numpy as np
import pandas as pd
import flowkit as fk
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

class SampleManualCompensation(fk.Sample):
    def __init__(self, *args, xml_path, **kwargs):
        super().__init__(*args, **kwargs)

        # Correct channel idx issues
        if self.pnn_labels[0]=='FS PEAK':
            self.fluoro_indices=[3,4,5,6,7,8,9,10,11,12]
            self.scatter_indices=[1,2]
        else:
            self.fluoro_indices=[2,3,4,5,6,7,8,9,10,11]
            self.scatter_indices=[0,1]

        self.compensation = self.read_compensation(xml_path)

    @staticmethod
    def read_compensation(xml_path: str) -> fk.Matrix:
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
        
        
        compensation_df = pd.DataFrame(generator).sort_values(by="S", key=natsort_keygen())

        label_mapping, channel_mapping = get_mappings(tree)

        compensation_df["S"] = compensation_df["S"].apply(lambda x: channel_mapping[x])
        compensation_df["C"] = compensation_df["C"].apply(lambda x: channel_mapping[x])

        p = compensation_df.pivot(index="S", columns="C", values="V").astype(float)
        p = p.sort_index(key=natsort_keygen()).reindex(natsorted(p.columns), axis=1).T
        p.fillna(0, inplace=True)
        np.fill_diagonal(p.values, 1)
    
        sources = p.index.to_list()
        fluorochromes = [label_mapping[el] for el in sources]
    
        matrix = fk.Matrix(p.values, sources, fluorochromes)

        return matrix


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
                samples[0], xml_path=xml_handle
            )

        os.remove(tmp_fcs_path)

    return sample
    
