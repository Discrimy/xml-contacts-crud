from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Work:
    address: str
    jobs: List[str]


@dataclass
class Contact:
    pk: Optional[int]
    firstname: str
    lastname: str
    surname: str
    address: str
    phone_numbers: List[str]
    works: List[Work]
    photos: List[str]

    @property
    def fio(self) -> str:
        return f'{self.surname} {self.firstname} {self.lastname}'
