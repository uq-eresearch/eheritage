#!/usr/bin/env python
#
# Generate peewee models like:
# pwiz.py -H localhost -u root -P 'password' -e mysql vhd
import json
import peewee
from vhd_tables import Places
from collections import OrderedDict


fields = [field[0] for field in Places._meta.get_sorted_fields()]


export_fields = (
    'id',
    'place_name',
    'location',
    'latitude',
    'longitude',
    'place_owner',
    'significance',
    'date_created',
    'last_updated'
)



def export_to_json():
    export_places = []
    for place in Places.select().limit(10):
        exp_place = OrderedDict()
        for field in export_fields:
            exp_place[field] = getattr(place, field)

        export_places.append(exp_place)

    print json.dumps(export_places, indent=4)


import lxml.etree as etree
import lxml.builder

ahpi_ns = 'http://www.heritage.gov.au/ahpi/heritage_places'

E = lxml.builder.ElementMaker(nsmap={None:ahpi_ns})

places = []

for place in Places.select().limit(10):
    x = E.heritage_place(
            E.name(place.place_name),
            E.state("VIC"),
            E.country("AUSTRALIA"),
            E.sos(place.significance),
            E.latitude(place.latitude),
            E.longitude(place.longitude),
            id=str(place.id))
    places.append(x)


ROOT = E.HERITAGE_LIST(*places, code="VIC")

print etree.tostring(ROOT, pretty_print=True, xml_declaration=True)



def export_to_xml():
    pass