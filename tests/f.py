import urllib2
from lxml import html


def setTestUp(url):
    response = urllib2.urlopen(url).read()
    tree = html.fromstring(response)
    paras = tree.xpath('//p[contains(@class, "cusisheaderdata")]')

    header = paras[0].text.split(" ")
    term = header[0].lower()

    for p in paras:
        if 'summer' in term:
            p.getparent().remove(p.xpath('following-sibling::table[1]')[0])
        if len(p.text) > 15:
            p.getparent().remove(p.xpath('following-sibling::table[1]')[0])
    tables = tree.xpath("//table")
    return tables
