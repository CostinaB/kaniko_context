#!/usr/bin/python
import os
from notebook.services.contents.filemanager import FileContentsManager
import sys
import json
from nbformat import reads
from base64 import b64decode
import subprocess as sp
from bdl_client.api.notebooks_public_api_controller_api import NotebooksPublicApiControllerApi
from bdl_client.rest import ApiException
from nbconvert.preprocessors import ExecutePreprocessor
from bdl_client.configuration import Configuration
from bdl_client.api_client import ApiClient
import nbformat

NBFORMAT_VERSION = 4

class ExecuteNotebook():
  api_key = sys.argv[1]

  def __init__(self):
    api_endpoint = sys.argv[2]
    configuration = Configuration()
    configuration.host = api_endpoint
    api_client = ApiClient(configuration)
    self.api = NotebooksPublicApiControllerApi(api_client)

  def get_notebook(self, notebook_name, notebook_version, datalake_id):
    try:
      result = self.api.get_notebook_by_datalake_id_and_version(self.api_key, datalake_id, notebook_name, notebook_version)
      notebook = self.notebook_model_from_db(result)
      content = FileContentsManager()
      content.save(notebook, '/notebook.ipynb')
    except ApiException as e:
      print(e.body)['message']

  def execute_notebook(self):
    with open('/notebook.ipynb') as f:
      nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=600, allow_errors=True)
    ep.preprocess(nb, {'metadata': {'path': '.'}})
    with open('/executed_notebook.ipynb', mode='wt') as f:
      nbformat.write(nb, f)

  def reads_base64(self, nb, as_version=NBFORMAT_VERSION):
    """
    Read a notebook from base64.
    """
    return reads(b64decode(nb).decode('utf-8'), as_version=as_version)

  def base_model(self, path):
    return {
      "name": path.rsplit('/', 1)[-1],
      "path": path,
      "writable": True,
      "last_modified": None,
      "created": None,
      "content": None,
      "format": None,
      "mimetype": None,
    }

  def notebook_model_from_db(self, record):
    """
    Build a notebook model from database record.
    """
    path = record.name
    model = self.base_model(path)
    model['type'] = 'notebook'
    model['last_modified'] = record.updated_timestamp_seconds
    model['created'] = record.created_timestamp_seconds
    content = self.reads_base64(record.content_base64_encoded)
    model['content'] = content
    model['format'] = 'json'
    return model

notebook_name = os.environ['NOTEBOOK_NAME']
notebook_version = os.environ['NOTEBOOK_VERSION']
datalake_id = os.environ['DATALAKE_ID']
execute = ExecuteNotebook()
execute.get_notebook(notebook_name, notebook_version, datalake_id)
execute.execute_notebook()