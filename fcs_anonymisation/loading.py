import xml.etree.ElementTree as ET
import numpy as np
import flowkit as fk
import pandas as pd

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
        
        matrix = fk.Matrix(p, detectors, fluorochromes)
        return matrix
