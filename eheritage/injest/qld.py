from lxml import etree

def parse_ahpi_xml(path):
    """
    Parses the AHPI XML export format of the queensland heritage register
    and calls a function with each heritage place.

    :param path: The location of a heritage_places xml file.
    """
    ns = {'hp': 'http://www.heritage.gov.au/ahpi/heritage_places'}

    tree = etree.parse(path)
    root = tree.getroot()

    for hp_element in root.xpath('//hp:heritage_place', namespaces=ns):
        hp = {
            "date_created": hp_element.get('date_created'),
            "date_modified": hp_element.get('date_modified'),
            "id": hp_element.get('id'),
            "name": hp_element.xpath('hp:name', namespaces=ns)[0].text,
            "addresses": [{
                "street_name": hp_element.xpath('hp:address', namespaces=ns)[0].text,
                "lga_name": hp_element.xpath('hp:lga', namespaces=ns)[0].text,
                "suburb": hp_element.xpath('hp:town', namespaces=ns)[0].text,
                "state": hp_element.xpath('hp:state', namespaces=ns)[0].text,
                "country": hp_element.xpath('hp:country', namespaces=ns)[0].text,
            }],
            "state": hp_element.xpath('hp:state', namespaces=ns)[0].text,
            "category": hp_element.xpath('hp:category', namespaces=ns)[0].text,
            "significance": hp_element.xpath('hp:sos', namespaces=ns)[0].text,
            "description": hp_element.xpath('hp:description', namespaces=ns)[0].text,
            "url": hp_element.xpath('hp:url', namespaces=ns)[0].text,
        }
        try:
            # import ipdb; ipdb.set_trace()
            lat = hp_element.xpath('hp:latitude', namespaces=ns)[0].text
            lon = hp_element.xpath('hp:longitude', namespaces=ns)[0].text
            hp['geolocation'] = {
                "lat": float(lat), "lon": float(lon)
            }
        except TypeError:
            print "error parsing lat/lon %s/%s" % (lat, lon)
            pass

        yield hp




if __name__ == "__main__":
    def myPrint(arg): print arg

    hp_filename = "/mnt/groups/maenad/activities/e-Heritage/QLD/heritage_list.xml"

    result = parse_ahpi_xml(hp_filename, myPrint)
    print result


