# Installation
All dependencies can be [installed from the requirements file](https://pip.pypa.io/en/stable/getting-started/#install-multiple-packages-using-a-requirements-file).

# Generate mock data for script testing

```python generate_mock_data.py```

Creates 20 analysis files from a fcs and its xml sidecar. `datapath` and xml/fcs file names must be set respectively in `config.yaml` and inside the script.

# Create anonymous directory
This command creates an `anonymous_fcs` directory from a directory containing .analysis files and an excel metadata file.

```python export_fcs --input_dir SENSITIVE_FCS_DIR --metadata METADATA_FILE.xslx```

Type `python export_fcs --help` to get all options. You can specify which columns should be kept by passing a path to a colspecs directory.
See `colspecs/mock_data` for an example configuration.

The naming scheme and directory structure are loosely inspired by the [BIDS standard](https://bids-specification.readthedocs.io/en/stable/index.html).