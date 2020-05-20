import papermill as pm
from pathlib import Path
import os, re, urllib, datetime

DEFAULT_VERSION = datetime.datetime.now().isoformat(timespec='milliseconds').replace(':', '.') + 'Z'

def _extract_dataset_name_from_log(output_text):
    m = re.search(r'kedro.io.data_catalog - INFO - Saving data to `(\w+)`', output_text)
    return m.group(1) if m else None

class NotebookExecuter:
    def __init__(self, catalog, input_path, output_path=None, parameters=None, versioned=False, version=DEFAULT_VERSION):
        self.__catalog = catalog
        self.__input_path = input_path
        self.__parameters = parameters
        self.__versioned = versioned
        self.__version = version
        self.__output_path = output_path or self.__get_default_output_path()

    def __call__(self, *args):
        nb = pm.execute_notebook(self.__input_path, self.__output_path, self.__parameters)
        dataset_names = [
            _extract_dataset_name_from_log(output['text'])
            for cell in nb['cells'] if 'outputs' in cell
            for output in cell['outputs'] if 'text' in output
        ]
        return {dataset_name: self.__catalog.load(dataset_name) for dataset_name in dataset_names if dataset_name}

    def __get_default_output_path(self):
        name, ext = os.path.splitext(os.path.basename(self.__input_path))
        if self.__parameters:
            name += '#' + urllib.parse.urlencode(self.__parameters)
        name += ext
        output_dir = Path(os.getenv('PAPERMILL_OUTPUT_DIR', ''))
        if self.__versioned:
            output_dir = output_dir / name / self.__version
            output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir / name)
