from xml.etree import ElementTree as ET

from database.entities import Contact, Work


def contact_to_xml(contact: Contact) -> ET.Element:
    entry = ET.Element('entry')
    entry.attrib['pk'] = str(contact.pk)
    ET.SubElement(entry, 'firstname').text = contact.firstname
    ET.SubElement(entry, 'lastname').text = contact.lastname
    ET.SubElement(entry, 'surname').text = contact.surname
    ET.SubElement(entry, 'address').text = contact.address
    home_tels = ET.SubElement(entry, 'home-tels')
    for phone_number in contact.phone_numbers:
        ET.SubElement(home_tels, 'home-tel').text = phone_number
    works = ET.SubElement(entry, 'works')
    for work in contact.works:
        work_element = ET.SubElement(works, 'work')
        jobs = ET.SubElement(work_element, 'jobs')
        for job in work.jobs:
            ET.SubElement(jobs, 'job').text = job
        ET.SubElement(work_element, 'work-address').text = work.address
    photos = ET.SubElement(entry, 'photos')
    for photo in contact.photos:
        ET.SubElement(photos, 'photo').text = photo
    return entry


def xml_to_contact(xml: ET.Element) -> Contact:
    return Contact(
        pk=int(xml.attrib['pk']),
        firstname=xml.find('firstname').text,
        lastname=xml.find('lastname').text,
        surname=xml.find('surname').text,
        address=xml.find('address').text,
        phone_numbers=[
            phone_number_element.text
            for phone_number_element in xml.findall('home-tels/home-tel')
        ],
        works=[
            Work(
                address=work_element.find('work-address').text,
                jobs=[
                    job_element.text for job_element in work_element.findall('jobs/job')
                ]
            ) for work_element in xml.findall('works/work')
        ],
        photos=[
            photo_element.text for photo_element in xml.findall('photos/photo')
        ],
    )
