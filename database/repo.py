from dataclasses import replace
from pathlib import Path
from typing import List, Optional
from xml.etree import ElementTree as ET

from database.parsers import xml_to_contact, contact_to_xml
from database.entities import Contact


def icontains(text: str, substring: str) -> bool:
    return substring.lower() in text.lower()


class ContactsXMLRepository:
    def __init__(self, xml_path: Path):
        self._xml_path = xml_path

    def get_all(self) -> List[Contact]:
        return [
            xml_to_contact(entry)
            for entry in ET.parse(self._xml_path).getroot().findall('entry')
        ]

    def get_by_pk(self, pk: int) -> Optional[Contact]:
        return next(
            (contact for contact in self.get_all() if contact.pk == pk),
            None
        )

    def save_all(self, contacts: List[Contact]) -> None:
        address_book_element = ET.Element('address-book')
        for contact in contacts:
            entry = contact_to_xml(contact)
            address_book_element.append(entry)
        ET.ElementTree(address_book_element).write(self._xml_path)

    def delete_by_pk(self, pk: int) -> None:
        filtered_contacts = [contact for contact in self.get_all() if contact.pk != pk]
        self.save_all(filtered_contacts)

    def copy_by_pk(self, pk: int) -> None:
        contact_to_copy = self.get_by_pk(pk)
        if contact_to_copy is None:
            raise ValueError(pk)

        all_contacts = self.get_all()
        contact_copy = replace(
            self.get_by_pk(pk),
            pk=max(contact.pk for contact in all_contacts) + 1
        )
        contacts = all_contacts + [contact_copy]
        self.save_all(contacts)

    def search(self, search_text: str) -> List[Contact]:
        return [
            contact for contact in self.get_all()
            if icontains(contact.fio, search_text)
            or icontains(contact.address, search_text)
            or any(icontains(phone_number, search_text) for phone_number in contact.phone_numbers)
            or any(
                icontains(work.address, search_text)
                or any(icontains(job, search_text) for job in work.jobs)
                for work in contact.works
            )
        ]

    def save(self, new_contact: Contact) -> None:
        saved = self.get_all()
        if new_contact.pk is None:
            new_contact = replace(
                new_contact,
                pk=max(contact.pk for contact in saved if contact.pk is not None) + 1
            )
            saved += [new_contact]
        else:
            saved = [
                new_contact if saved_contact.pk == new_contact.pk else saved_contact
                for saved_contact in saved
            ]
        self.save_all(saved)
