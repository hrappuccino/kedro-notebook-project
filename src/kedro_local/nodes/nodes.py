import papermill as pm
import os, re, json, hashlib, datetime

def _extract_dataset_name_from_log(output_text):
    m = re.search(r'kedro.io.data_catalog - INFO - Saving data to `(\w+)`', output_text)
    return m.group(1) if m else None

class NotebookExecuter:
    def __init__(self, catalog, input_path, output_path=None, parameters=None):
        self.__catalog = catalog
        self.__input_path = input_path
        self.__parameters = parameters
        self.__output_path = output_path or self.__get_default_output_path()

    def __call__(self, *args):
        nb = pm.execute_notebook(self.__input_path, self.__output_path, self.__parameters)
        dataset_names = [_extract_dataset_name_from_log(output['text']) for cell in nb['cells'] for output in cell['outputs']]
        return [self.__catalog.load(dataset_name) for dataset_name in dataset_names if dataset_name]

    def __get_default_output_path(self):
        name, ext = os.path.splitext(os.path.basename(self.__input_path))
        parameters_hash = hashlib.sha1(json.dumps(self.__parameters, sort_keys=True).encode('utf-8')).hexdigest()
        timestamp = datetime.datetime.now().isoformat()
        return os.path.join(os.environ['PAPERMILL_OUTPUT_DIR'], f'{name}_{parameters_hash}_{timestamp}{ext}')
