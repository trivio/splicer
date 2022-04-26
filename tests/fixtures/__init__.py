from splicer import DataSet

from .employee_adapter import EmployeeAdapter
from .mock_adapter import MockAdapter


def mock_data_set():
    dataset = DataSet()
    dataset.add_adapter(MockAdapter())
    dataset.add_adapter(EmployeeAdapter())
    return dataset
