# import requests
import lxml.html
import sys
import json
import os
import re

def read_qld_html(filename):
    obj = {}
    with open(filename) as f:
        data = f.read()
        dom = lxml.html.fromstring(data)

        for el in dom.xpath("//div[@class='article']//td[@class='formLayoutLabelTD']"):
            name = el.findtext('.').strip()
            # print name

            # if name == 'Place Components':
                # import ipdb; ipdb.set_trace()

            parent = el.getparent()
            contentEl = parent.xpath("td")[1]
            content = [contentEl.findtext('.').strip()]
            # content = [c.findtext('.').strip() for c in parent.xpath("td")[1:]]
            content += [m.tail.strip() for m in contentEl.getchildren() if m.tail.strip()]
            obj[name] = content
            # print content

            # print
    return obj

def extract_dates(date_string):
    dates = re.findall(r'\d\d\d\d', date_string) + [None, None]
    return dates[:2]



def transform_to_eheritage(data_in):
    data_out = {}
    data_out['group'] = data_in.get('Place Type', [])
    data_out['place_category'] = data_in.get('Place Category', [])
    start, end = extract_dates(data_in.get('Construction Period', [''])[0])
    data_out['construction_start'] = start
    data_out['construction_end'] = end

    return data_out


def load_extra(public_url, basename):
    filename = public_url.split('/')[-1]
    filename = basename + filename

    return transform_to_eheritage(read_qld_html(filename))


def read_all(dir_name):
    all_data = []
    for root, dirs, files in os.walk(dir_name):
        for filename in files:
            filepath = os.path.join(root, filename)
            data = read_qld_html(filepath)
            all_data.append(data)
    return all_data



if __name__ == "__main__":
    dir_name = sys.argv[1]
    all_data = read_all(dir_name)

    output_file = sys.argv[2]
    with open(output_file, 'w') as f:
        json.dump(all_data, f)


    # filename = sys.argv[1]
    # data = read_qld_html(filename)

    # print json.dumps(data, indent=1)