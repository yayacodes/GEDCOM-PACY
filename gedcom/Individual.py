import attr
from datetime import datetime


@attr.s
class Individual:
    id: str = attr.ib()
    name: str = attr.ib(default=None)
    sex: str = attr.ib(default=None)
    birthday: datetime = attr.ib(default=None)
    death = datetime = attr.ib(default=None)
    child = attr.ib(default=None)
    spouse = attr.ib(default=None) # DEPRECATED -- Old usage of spouse
    spouses = attr.ib(factory=list) # List of all families for which they are a spouse
    kind = 'INDI'

    @property
    def alive(self) -> bool:
        return False if self.death else True

    @property
    def age(self) -> int:
        if self.alive:
            return int((datetime.now() - self.birthday).days / 365)
        else:
            return int((self.death - self.birthday).days / 365)