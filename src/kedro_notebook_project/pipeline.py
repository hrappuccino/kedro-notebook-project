from kedro.pipeline import Pipeline, node
from kedro_local.nodes import *
import yaml

def create_pipelines(catalog, **kwargs):
    with open('conf/base/pipelines.yml') as f:
        pipelines_ = yaml.safe_load(f)

    pipelines = {
        pipeline_name: Pipeline([
            node(
                NotebookExecuter(catalog, **node_['nb']),
                node_['inputs'] if 'inputs' in node_ else None,
                {output: output for output in node_['outputs']} if 'outputs' in node_ else None,
                name=node_name,
            ) for node_name, node_ in nodes_.items()
        ]) for pipeline_name, nodes_ in pipelines_.items()
    }

    for pipeline_ in list(pipelines.values()):
        if '__default__' not in pipelines:
            pipelines['__default__'] = pipeline_
        else:
            pipelines['__default__'] += pipeline_

    return pipelines
