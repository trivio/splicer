from splicer import DataSet, Query

from .mock_server import  MockServer
from .employee_server import EmployeeServer

def mock_data_set():
  dataset = DataSet()
  dataset.add_server(MockServer())
  dataset.add_server(EmployeeServer())
  return dataset
