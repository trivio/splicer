from splicer import DataSet

from .mock_adapter import  MockAdapter
from .employee_adapter import EmployeeAdapter

def mock_data_set():
  dataset = DataSet()
  dataset.add_adapter(MockAdapter())
  dataset.add_adapter(EmployeeAdapter())
  return dataset
