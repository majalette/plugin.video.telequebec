# -*- coding: utf-8 -*-

import os
import sys
from kodi_six import xbmc, xbmcaddon, xbmcgui, xbmcvfs
from xbmcaddon import Addon

addon = Addon('plugin.video.telequebec')
addon_cache_basedir = os.path.join(xbmcvfs.translatePath(addon.getAddonInfo('path')).decode('utf-8'),".cache")

if sys.argv[1].lower() == "full":
    print("["+addon.getAddonInfo('name')+"] deleting full cache")
    for root, dirs, files in os.walk(addon_cache_basedir):
        for file in files:
            xbmcvfs.delete(os.path.join(root,file))
    xbmcgui.Dialog().ok(addon.getAddonInfo('name'), addon.getLocalizedString(32108),addon.getLocalizedString(32109))

