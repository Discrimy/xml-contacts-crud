import re
from pathlib import Path
from typing import List

from flask import Flask, render_template, redirect, request

from database.entities import Contact, Work
from database.repo import ContactsXMLRepository

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

contacts_repo = ContactsXMLRepository(xml_path=Path('address-book.xml'))


@app.route("/", methods=['GET'])
def contacts_list():
    search_text = request.args.get('q')
    if search_text is None:
        contacts = contacts_repo.get_all()
    else:
        contacts = contacts_repo.search(search_text)
    return render_template(
        'index.html',
        contacts=contacts,
        search_text=search_text or ''
    )


@app.route("/<int:pk>/delete/", methods=['POST'])
def contact_delete(pk: int):
    contacts_repo.delete_by_pk(pk)
    return redirect('/')


@app.route('/<int:pk>/copy/', methods=['POST'])
def contact_copy(pk: int):
    contacts_repo.copy_by_pk(pk)
    return redirect('/')


@app.route('/new/')
def contact_new():
    return render_template(
        'form.html',
        pk='',
        firstname='',
        lastname='',
        surname='',
        address='',
        phone_numbers='',
    )


def _format_works(works: List[Work]) -> str:
    return '\n\n'.join(
        '\n'.join([work.address, *work.jobs])
        for work in works
    )


@app.route('/<int:pk>/edit/')
def contact_edit(pk: int):
    contact = contacts_repo.get_by_pk(pk)
    return render_template(
        'form.html',
        pk=contact.pk,
        firstname=contact.firstname,
        lastname=contact.lastname,
        surname=contact.surname,
        address=contact.address,
        phone_numbers='\n'.join(contact.phone_numbers),
        works=_format_works(contact.works),
        photos='\n'.join(contact.photos),
    )


@app.route('/save/', methods=['POST'])
def contact_save():
    try:
        pk = int(request.form['pk'])
    except ValueError:
        pk = None
    if request.form['phone_numbers'].strip() == '':
        phone_numbers = []
    else:
        phone_numbers = request.form['phone_numbers'].strip().splitlines()

    if request.form['works'].strip() == '':
        works = []
    else:
        works_str = [
            work_str.splitlines()
            for work_str
            in re.split(r'\n\r?\n\r?', request.form['works'].strip())
        ]
        works = [
            Work(address=address, jobs=jobs)
            for (address, *jobs) in works_str
        ]

    if request.form['photos'].strip() == '':
        photos = []
    else:
        photos = request.form['photos'].splitlines()

    contact = Contact(
        pk=pk,
        firstname=request.form['firstname'],
        lastname=request.form['lastname'],
        surname=request.form['surname'],
        address=request.form['address'],
        phone_numbers=phone_numbers,
        works=works,
        photos=photos,
    )
    contacts_repo.save(contact)
    return redirect('/')
