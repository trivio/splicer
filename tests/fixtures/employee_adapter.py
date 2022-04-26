from datetime import date

from splicer.adapters.dict_adapter import DictAdapter

employee_records = [
    dict(employee_id=1234, full_name="Tom Tompson", employment_date=date(2009, 1, 17)),
    dict(
        employee_id=4567,
        full_name="Sally Sanders",
        employment_date=date(2010, 2, 24),
        manager_id=1234,
    ),
    dict(
        employee_id=8901,
        full_name="Mark Markty",
        employment_date=date(2010, 3, 1),
        manager_id=1234,
        roles=("sales", "marketing"),
    ),
]


class EmployeeAdapter(DictAdapter):
    def __init__(self):
        super(EmployeeAdapter, self).__init__(
            employees=dict(
                schema=dict(
                    fields=[
                        dict(name="employee_id", type="INTEGER"),
                        dict(name="full_name", type="STRING"),
                        dict(name="employment_date", type="DATE"),
                        dict(name="manager_id", type="INTEGER"),
                        dict(name="roles", type="STRING", mode="REPEATED"),
                    ]
                ),
                rows=employee_records,
            )
        )
