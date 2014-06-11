# import requests
import lxml.html
import sys


with open(sys.argv[1]) as f:
    data = f.read()
    dom = lxml.html.fromstring(data)

    for el in dom.xpath("//div[@class='article']//td[@class='formLayoutLabelTD']"):
        name = el.findtext('.').strip()
        print name

        # if name == 'Place Components':
            # import ipdb; ipdb.set_trace()

        parent = el.getparent()
        contentEl = parent.xpath("td")[1]
        content = [contentEl.findtext('.').strip()]
        # content = [c.findtext('.').strip() for c in parent.xpath("td")[1:]]
        content += [m.tail.strip() for m in contentEl.getchildren() if m.tail.strip()]
        print content

        print


