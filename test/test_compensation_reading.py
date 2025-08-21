"""
We are storing compensation as spill string and as dataframe.
We want to make sure that they match
"""

import numpy as np
from flowutils.compensate import parse_compensation_matrix
from fcs_anonymisation.loading import SampleManualCompensation, read_analysis


XML_PATH = "mock_dataset/BDX-PQOXX59186921 Moele bla bla-bla_bla 7188.analysis"
def test_compensation_is_consistent():
    sample = read_analysis(XML_PATH)
    matrix = sample.compensation_matrix
    spill_str = sample.spill_string
    sensors = sample.compensation_df.S.unique()
    reconstructed_arr = parse_compensation_matrix(spill_str, sensors)
    # First row in reconstructed array is an index
    assert np.all(reconstructed_arr[1:, :] == matrix.matrix)

