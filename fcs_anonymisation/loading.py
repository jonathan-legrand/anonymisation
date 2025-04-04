import xml.etree.ElementTree as ET
from zipfile import ZipFile
import re
import os
import tempfile

import numpy as np
import pandas as pd
import flowkit as fk
from flowio import read_multiple_data_sets


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

    def read_compensation(self, xml_path):
        tree = ET.parse(xml_path)
        retrieve_list = tree.findall(".//Compensation")
        assert len(retrieve_list) == 1, "That's weird"
        compensation_element = retrieve_list[0]

        detectors = [self.pnn_labels[i] for i in self.fluoro_indices]
        fluorochromes = [self.pns_labels[i] for i in self.fluoro_indices]

        channels = [pn.split(" ")[0] for pn in detectors]
        generator = (child.attrib for child in compensation_element.find("S"))
        compensation_df = pd.DataFrame(generator).sort_values(by="S")
        p = compensation_df.pivot(index="S", columns="C", values="V").astype(float)
        p = p.loc[channels, channels].values
        p = np.where(np.isnan(p), 0, p)
        np.fill_diagonal(p, 1)
        matrix = fk.Matrix(p, detectors, fluorochromes)
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
    
