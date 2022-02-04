# -*- coding: utf-8 -*-
# version 3.2.2 - By dualB

import os, time, sys, io
from kodi_six import xbmcaddon, xbmcvfs, xbmc
from . import log, html

ADDON = xbmcaddon.Addon()

ADDON_CACHE_BASEDIR = os.path.join(xbmcvfs.translatePath(ADDON.getAddonInfo('path')), ".cache")
ADDON_CACHE_TTL = float(ADDON.getSetting('CacheTTL').replace("0", ".5").replace("73", "0"))

if not os.path.exists(ADDON_CACHE_BASEDIR):
    os.makedirs(ADDON_CACHE_BASEDIR)

if sys.version >= "2.5":
    from hashlib import md5 as _hash
else:
    from md5 import new as _hash


def is_cached_content_expired(last_update):
    """ function docstring """
    expired = time.time() >= (last_update + (ADDON_CACHE_TTL * 60**2))
    return expired


def get_cached_content(path,verified=True,headers=[]):
    """ function docstring """
    content = None
    
    try:
        filename = get_cached_filename(path)
        if os.path.exists(filename) and not is_cached_content_expired(os.path.getmtime(filename)):
            log.log('Lecture en CACHE du contenu suivant :' + path)
            content = open(filename).read()
        else:
            log.log('Lecture en LIGNE du contenu suivant :' + path)
            content = html.get_url_txt(path,verified,headers)
            if len(content)>0:
                try:
                    if sys.version >= "3":
                        file(filename, "w").write(content) # cache the requested web content
                    else:
                        open(filename, "w").write(content) # cache the requested web content
                except Exception:
                    log.log('Impossible d ecrire le contenu pour le conserver en cache')

    except Exception:
        log.log('ERREUR - Impossible de trouver le contenu suivant :' + path)
        return None
    return content

def get_cached_filename(path):
    """ function docstring """
    utfName = repr(path).encode('utf-8')
    filename = "%s" % _hash(utfName).hexdigest()
    return os.path.join(ADDON_CACHE_BASEDIR, filename)
