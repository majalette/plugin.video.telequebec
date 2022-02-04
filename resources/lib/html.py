# -*- coding: utf-8 -*-
# version 3.2.2 - By dualB

import sys, re, socket, ssl
from kodi_six import xbmc
from . import log

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import unquote, quote, quote_plus, unquote_plus, urljoin, urlparse
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
else:
    # Python 2 stuff
    from urlparse import urljoin, urlparse
    from urllib import quote_plus, unquote_plus, unquote, quote
    from urllib2 import Request, urlopen, HTTPError, URLError

def get_url_txt(the_url,verified=True,headers=[]):
    """ function docstring """
    log.log('Tentative de connection a : ' + the_url)
    req = Request(the_url)
    
    for header in headers:
        req.add_header(header['key'],header['value'])

    req.add_header(\
                       'User-Agent', \
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'\
                       )
    req.add_header('Accept-Charset', 'utf-8')
    
    try:
        context = None
        if not verified:
            log.log('Requete en SSL NON VERIFIE')
            context = ssl._create_unverified_context()
        response = urlopen(req,context=context)
        link = response.read()
        link = quote(link)
        link = unquote(link)
        response.close()
        return link
    except HTTPError as e:
        log.log('HTTPError = ' + str(e.code))
        log.log(e.reason)
        return ''
    except URLError as e:
        log.log('URLError = ' + str(e.reason))
        return ''
    except Exception as e:
        log.log('Exception')
        log.log(e)
        return ''


def is_network_available(url):
    """ function docstring """
    try:
        # see if we can resolve the host name -- tells us if there is a DNS listening
        host = socket.gethostbyname(url)
        # connect to the host -- tells us if the host is actually reachable
        srvcon = socket.create_connection((host, 80), 2)
        srvcon.close()
        return True
    except socket.error:
        return False

    
