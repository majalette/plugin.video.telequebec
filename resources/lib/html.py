# -*- coding: utf-8 -*-
# version 3.2.2 - By dualB

import re, socket, urllib2, xbmc, ssl
from log import log

def get_url_txt(the_url,verified=True,headers=[]):
    """ function docstring """
    log('Tentative de connection a : ' + the_url)
    req = urllib2.Request(the_url)
    
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
            log('Requete en SSL NON VERIFIE')
            context = ssl._create_unverified_context()
        response = urllib2.urlopen(req,context=context)
        link = response.read()
        link = urllib2.quote(link)
        link = urllib2.unquote(link)
        response.close()
        return link
    except urllib2.HTTPError, e:
        log('HTTPError = ' + str(e.code))
        log(e.reason)
        return ''
    except urllib2.URLError, e:
        log('URLError = ' + str(e.reason))
        return ''
    except httplib.HTTPException, e:
        log('HTTPException')
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

    
