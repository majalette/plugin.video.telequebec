# -*- coding: utf-8 -*-

# version 3.2.2 - By dualB

import os, sys, traceback, simplejson
import xbmcaddon, xbmcplugin, xbmcvfs

from resources.lib.log import log
from resources.lib import content, navig

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import quote_plus, unquote_plus, unquote
else:
    # Python 2 stuff
    from urllib import quote_plus, unquote_plus, unquote

ADDON = xbmcaddon.Addon()



def get_params():
    """ function docstring """
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params)-1] == '/':
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for k in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[k].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

def set_content(content):
    """ function docstring """
    xbmcplugin.setContent(int(sys.argv[1]), content)
    return

def set_sorting_methods(mode):
    pass
    #if xbmcaddon.Addon().getSetting('SortMethodTvShow') == '1':
    #    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    #    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)
    #return

PARAMS = get_params()

URL = None
MODE = None
SOURCE_ID = ''
FILTERS = ''
filtres = {}

try:
    URL = unquote_plus(PARAMS["url"])
    log("PARAMS['url']:"+URL)
except Exception:
    pass
try:
    MODE = int(PARAMS["mode"])
    log("PARAMS['mode']:"+str(MODE))
except Exception:
    pass
try:
    FILTERS = unquote_plus(PARAMS["filters"])
    log("PARAMS['filters']:"+str(FILTERS))
except Exception:
    FILTERS = content.FILTRES
try:
    SOURCE_ID = unquote_plus(PARAMS["sourceId"])
    log("PARAMS['sourceId']:"+str(SOURCE_ID))
except Exception:
    pass

filtres = simplejson.loads(FILTERS)

if SOURCE_ID !='':
    navig.jouer_video(URL,SOURCE_ID)

elif MODE == 99:
    ADDON.openSettings()
    
else:
    navig.peupler(filtres)
    set_content('Videos')

if MODE != 99:
    set_sorting_methods(MODE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if MODE != 4 and xbmcaddon.Addon().getSetting('DeleteTempFiFilesEnabled') == 'true':
    PATH = xbmcvfs.translatePath('special://temp').decode('utf-8')
    FILENAMES = next(os.walk(PATH))[2]
    for i in FILENAMES:
        if ".fi" in i:
            os.remove(os.path.join(PATH, i))

