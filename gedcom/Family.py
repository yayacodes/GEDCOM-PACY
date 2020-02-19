import attr
from datetime import datetime


@attr.s
class Family:
    id: str = attr.ib()
    married: datetime = attr.ib(default=None)
    divorced: datetime = attr.ib(default=None)
    husband_id: str = attr.ib(default=None)
    husbandName: str = attr.ib(default=None)
    wife_id: str = attr.ib(default=None)
    wife_name: str = attr.ib(default=None)
    children: list = attr.ib(factory=list)
    kind = 'FAM'
