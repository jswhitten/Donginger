import json
import urllib2
from urllib import urlencode
from lxml import etree, html

class Plugin(object):

    def __init__(self, dong, conf):
        self.dong = dong
        self.conf = conf

    def build_query(self, url, params=None, get_method=None):
        if params:
            query_string = urlencode(params)
            if url.find('?') > -1:
                request = urllib2.Request(url + '&' + query_string)
            else:
                request = urllib2.Request(url + '?' + query_string)
        else:
            request = urllib2.Request(url)

        if get_method is not None:
            request.get_method = lambda: get_method

        opener = urllib2.build_opener()
        return opener.open(request)

    def get_head(self, url):
        return self.build_query(url, get_method='HEAD').read()

    def get_html(self, url, params=None, get_method=None):
        return html.fromstring(self.build_query(
            url, params, get_method).read())

    def get_json(self, url, params=None):
        return json.loads(self.build_query(url, params).read())

    def get_json_https(self, url, params=None):
        httpsha = urllib2.HTTPSHandler()
        opener = urllib2.build_opener(httpsha)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        uobj = opener.open(url)
        return json.loads(uobj.read())

    def get_xml(self, url, params=None):
        return etree.fromstring(self.build_query(url, params).read())

    def unescape(self, s):
        if not s.strip():
            return s
        return html.fromstring(s).text_content()

    def fromstring(self, text):
        return html.fromstring(text).text_content()
