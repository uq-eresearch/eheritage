from sqlalchemy import create_engine, MetaData, text
import json

import MySQLdb, MySQLdb.cursors

conn = MySQLdb.connect(user="vhd", passwd="vhd", db="vhd", cursorclass=MySQLdb.cursors.SSDictCursor, charset="utf8")
cursor = conn.cursor()

engine = create_engine("mysql+mysqldb://vhd:vhd@localhost/vhd?charset=utf8&use_unicode=0")


def test():
    everything_query = """
    select places.id, places.place_name, places.location, places.vhr_number, places.significance, places.longitude, places.latitude, 
    act_categories.act_category_name,
    addresses.street_number, addresses.street_name, addresses.suburb, addresses.state, addresses.postcode, lga_names.lga_name,
    architects.architect_name,
    architectural_styles.architectural_style_name,
    constructions.construction_start, constructions.construction_end
    from places

    JOIN act_categories_places on places.id = act_categories_places.place_id
    JOIN act_categories on act_categories_places.act_category_id = act_categories.id

    JOIN status_names ON places.status_id = status_names.id
    JOIN place_owners ON status_names.place_owner_id = place_owners.id

    LEFT JOIN addresses on places.id = addresses.place_id
    LEFT JOIN lga_names on addresses.lga_name_id = lga_names.id

    LEFT JOIN architects_places on places.id = architects_places.place_id
    LEFT JOIN architects on architects_places.architect_id = architects.id

    LEFT JOIN architectural_styles_places on places.id = architectural_styles_places.place_id
    LEFT JOIN architectural_styles on architectural_styles_places.place_id = architectural_styles.id

    LEFT JOIN constructions on places.id = constructions.place_id

    ORDER BY places.id
    LIMIT 1"""

    result = engine.execute(everything_query)
    for row in result:
        print(dict(row))


def get_number_of_places():
    """Retrieve the total number of Victorian Heritage Places"""
    result = engine.execute("SELECT COUNT(*) FROM places")
    num = result.first()[0]

    return num



def get_addresses(place_id):
    addresses_q = """SELECT street_number, street_name, suburb, state,
                            postcode, lga_names.lga_name
                     FROM addresses a
                     LEFT JOIN lga_names ON a.lga_name_id = lga_names.id
                     WHERE place_id = :place_id"""
    addresses = engine.execute(text(addresses_q), place_id=place_id)
    return [dict(address) for address in addresses]

def get_act_categories(place_id):
    act_categories_q = """SELECT act_category_name
                          FROM act_categories_places acp
                          JOIN act_categories ac ON acp.act_category_id = ac.id
                          WHERE place_id = :place_id"""
    act_categories = engine.execute(text(act_categories_q), place_id=place_id)
    return [act_category[0] for act_category in act_categories]

def get_architects(place_id):
    architects_q = """SELECT architect_name
                      FROM architects_places ap
                      JOIN architects ON ap.architect_id = architects.id
                      WHERE place_id = :place_id"""
    architects = engine.execute(text(architects_q), place_id=place_id)
    return [architect_name[0] for architect_name in architects]

def get_architectural_styles(place_id):
    architectural_styles_q = \
        """SELECT architectural_style_name
           FROM architectural_styles_places asp
           JOIN architectural_styles as ON asp.architectural_style_id = as.id
           WHERE place_id = :place_id"""
    architectural_styles = engine.execute(text(architectural_styles_q),
                                          place_id=place_id)
    return [architectural_style_name[0]
            for architectural_style_name in architectural_styles]

def get_item_categories(place_id):
    item_categories_q = """SELECT item_category_name
                          FROM item_categories_places, item_groups_name
                          JOIN item_categories on item_categories_places.item_category_id = item_categories.id
                          JOIN item_groups on item_categories_places.item_group_id = item_groups.id
                          WHERE place_id = :place_id"""
    item_categories = engine.execute(text(item_categories_q), place_id=place_id)
    return [item_category_name[0] for item_category_name in item_categories]

def massage_before_indexing(place):
    place['state'] = 'VIC'
    place['place_id'] = place['id']
    place['url'] = u"http://vhd.heritage.vic.gov.au/vhd/heritagevic#detail_places;%d" % place['id']
    place['country'] = 'Australia'
    place['name'] = place['place_name']

    for address in place['addresses']:
        address['state'] = 'VIC'


    try:
        place['geolocation'] = {
            'lat': float(place['latitude']),
            'lon': float(place['longitude'])
        }
    except TypeError:
        pass
    del(place['latitude'])
    del(place['longitude'])



def all_places():
    """Generator function for returning all victorian places
    """


    places_query = \
    """SELECT places.id, places.place_name, places.location,
       places.significance, places.vhr_number, places.longitude,
       places.latitude, constructions.construction_start,
       constructions.construction_end, places.nat_trust_listing_number,
       FROM places
       LEFT JOIN constructions ON places.id = constructions.place_id
    """

    result = cursor.execute(places_query)
    for place in cursor:
        row_id = place['id']
        place['addresses'] = get_addresses(row_id)
        place['act_categories'] = get_act_categories(row_id)
        place['architects'] = get_architects(row_id)
        place['architectural_styles'] = get_architectural_styles(row_id)

        massage_before_indexing(place)
#    print(json.dumps(place, indent=4))
        yield place







#places_table = meta.tables['places']
#results = engine.execute(places_table.select().limit(10))

