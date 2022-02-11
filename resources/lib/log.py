# -*- coding: utf-8 -*-
# version 3.2.2 - By dualB

import xbmc, xbmcaddon

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[ Tele-Quebec ]: ' +msg)
        
