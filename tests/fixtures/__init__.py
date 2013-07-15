from insitu import DataSet, Query

from fixtures.mock_server import  MockServer

def mock_data_set():
  dataset = DataSet()
  server = MockServer()
  dataset.add_server(server)
  return dataset
