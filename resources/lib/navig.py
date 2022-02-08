# -*- coding: utf-8 -*-
# version 3.2.2 - By dualB

import sys, re
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui
from . import log, parse, content, cache

try:
    import json
except ImportError:
    import simplejson as json

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import quote_plus, unquote, quote
    from urllib.request import Request, urlopen
else:
    # Python 2 stuff
    from urllib import quote_plus, unquote, quote
    from urllib2 import Request, urlopen

ADDON = xbmcaddon.Addon()
ADDON_IMAGES_BASEPATH = ADDON.getAddonInfo('path')+'/resources/media/images/'
ADDON_FANART = ADDON.getAddonInfo('path')+'/resources/fanart.jpg'

__handle__ = int(sys.argv[1])

def peupler(filtres):
    if filtres['content']['mediaBundleId']>0:
        ajouterItemAuMenu(parse.ListeVideosGroupees(filtres))
    else:
        if filtres['content']['genreId'] == "":
            filtres['content']['genreId'] = 0

        genreId = int(filtres['content']['genreId'])
        if genreId==-2:
            ajouterItemAuMenu(content.dictOfPopulaires(filtres))
        elif genreId>=-23 and genreId<=-21:
            ajouterItemAuMenu(content.get_liste_populaire(filtres))
        elif genreId!=0:
            ajouterItemAuMenu(content.get_liste_emissions(filtres))
        else:
            ajouterLive()
            ajouterItemAuMenu(content.dictOfMainDirs(filtres))
            ajouterItemAuMenu(content.dictOfGenres(filtres))
           
def ajouterLive():
    text = 'Télé-Québec - EN DIRECT'
    liz = xbmcgui.ListItem(text)
    liz.setArt({ 'thumb' : ADDON.getAddonInfo('path')+'/resources/icon.png' } )
    liz.setInfo(  type="Video",infoLabels={"Title":'[I][COLOR cyan]'+text+'[/COLOR][/I]', "plot":'Télé-Québec en direct.'  })
    setFanart(liz,ADDON_FANART)
    liz.setProperty('IsPlayable', 'true')
    entry_url = sys.argv[0]+"?url=live&sourceId=live"
    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=False)


def ajouterItemAuMenu(items):
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DATE)

    for item in items:
        if item['isDir'] == True:
            ajouterRepertoire(item)

        else:
            ajouterVideo(item)
            xbmc.executebuiltin('Container.SetViewMode('+str(xbmcplugin.SORT_METHOD_DATE)+')')
            #xbmc.executebuiltin('Container.SetSortDirection(0)')


def ajouterRepertoire(show):
    nom = show['nom']
    url = show['url']
    iconimage =show['image']
    resume = remove_any_html_tags(show['resume'])
    fanart = show['fanart']
    filtres = show['filtres']

    if resume=='':
        resume = unquote(ADDON.getAddonInfo('id') +' v.'+ADDON.getAddonInfo('version'))
    if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
        resume = '[B]'+nom+'[/B][CR]' + unquote(resume)
    if iconimage=='':
        iconimage = ADDON_IMAGES_BASEPATH+'default-folder.png'

    """ function docstring """
    entry_url = sys.argv[0]+"?url="+url+\
        "&mode=1"+\
        "&filters="+quote(json.dumps(filtres))

    is_it_ok = True
    liz = xbmcgui.ListItem(nom)
    liz.setArt({ 'thumb' : iconimage } )

    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title": nom,\
            "plot":resume
        }\
    )
    setFanart(liz,fanart)

    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=True)

    return is_it_ok

def setFanart(liz,fanart):
    if ADDON.getSetting('FanartEnabled') == 'true':
        if ADDON.getSetting('FanartEmissionsEnabled') == 'true':
            liz.setProperty('fanart_image', fanart)
        else:
            liz.setProperty('fanart_image', ADDON_FANART)
    else:
        pass


def ajouterVideo(show):
    name = show['nom']
    the_url = show['url']
    iconimage = show['image']
    finDisponibilite = show['endDateTxt']

    resume = remove_any_html_tags(show['resume'] +'[CR][CR]' + finDisponibilite)
    duree = show['duree']
    fanart = show['fanart']
    sourceId = show['sourceId']
    annee = show['startDate'][:4]
    premiere = show['startDate']
    episode = show['episodeNo']
    saison = show['seasonNo']

    is_it_ok = True
    entry_url = sys.argv[0]+"?url="+quote_plus(the_url)+"&sourceId="+(sourceId)

    if resume != '':
        if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
            resume = '[B]'+name.lstrip()+'[/B]'+'[CR]'+resume.lstrip()
    else:
        resume = name.lstrip()

    liz = xbmcgui.ListItem(\
        # remove_any_html_tags(name), iconImage=ADDON_IMAGES_BASEPATH+"default-video.png", thumbnailImage=iconimage)
        remove_any_html_tags(name))
    #liz.setArt({'icon': ADDON_IMAGES_BASEPATH+"default-video.png"})
    liz.setArt({ 'thumb' : iconimage } )
    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title":remove_any_html_tags(name),\
            "Plot":remove_any_html_tags(resume, False),\
            "Duration":duree,\
            "Year":annee,\
            "Premiered":premiere,\
            "Episode":episode,\
            "Season":saison}\
    )
    liz.addContextMenuItems([('Informations', 'Action(Info)')])
    setFanart(liz,fanart)
    liz.setProperty('IsPlayable', 'true')
    
    #Assumé que tous les liens sont pour Brightcove
    liz.setContentLookup(False)
    #deprecated inputstreamaddon prop was causing playback failure
    liz.setProperty('inputstream', 'inputstream.adaptive')
    liz.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    liz.setMimeType('application/xml+dash')
    

    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=False)
    return is_it_ok

RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_AFTER_CR = re.compile(r'\n.*')

def jouer_live():
    uri = liveStreamURL()
    if uri:
        item = xbmcgui.ListItem('Télé-Québec - EN DIRECT', path=uri)
        xbmcplugin.setResolvedUrl(__handle__,True, item)
    else:
        xbmc.executebuiltin("Notification(Aucun lien disponible,Incapable d'obtenir le lien du vidéo,5000)")

def liveStreamURL():
    config = getBrightcoveConfig()
    header = {'key':'Accept','value':'application/json;pk=%s'% config['key'] }
    a= cache.get_cached_content('https://bcovlive-a.akamaihd.net/575d86160eb143458d51f7ab187a4e68/us-east-1/6101674910001/playlist.m3u8',True,[header])
    return 'https://bcovlive-a.akamaihd.net/575d86160eb143458d51f7ab187a4e68/us-east-1/6101674910001/' + obtenirMeilleurStream(a,'profile')
   
def jouer_video(url,media_uid):
    #import web_pdb; web_pdb.set_trace()
    if "live" in url:
        jouer_live()
    else:
        """ function docstring """
        ref = re.split('/',url)
        refID = ref[len(ref)-1]

      
        video_json = json.loads(cache.get_cached_content('https://mnmedias.api.telequebec.tv/api/v4/player/%s' % refID))
        thumbnail_url = content.getImage(video_json['imageUrlTemplate'], '320', '180')
        
        uri = getURI(video_json,refID)
        if uri:
            item = xbmcgui.ListItem(\
                video_json['title'],\
                path=uri)
            item.setArt({'icon': thumbnail_url})
            play_item = xbmcgui.ListItem(path=uri)
            xbmcplugin.setResolvedUrl(__handle__,True, item)
        else:
            xbmc.executebuiltin('Notification(Aucun lien disponible,Incapable d\'obtenir le lien du vidéo,5000)')

def getURI(video_json,refID):
    streams = video_json['streamInfos']
    #Priorité au lien Brightcove
    #Retiré la lecture des liens Limelight
    for stream in streams:
        if stream['source']=='Brightcove':
            return m3u8BC(stream['sourceId'])       
    
def m3u8BC(sourceId):
    config = getBrightcoveConfig()
    log.log('KEY : %s' % config['key'])
    log.log('Ad_Config_ID : %s' %config['ad'])
    header = {'key':'Accept','value':'application/json;pk=%s'% config['key'] }
    a= json.loads(cache.get_cached_content('https://edge.api.brightcove.com/playback/v1/accounts/6150020952001/videos/%s?ad_config_id=%s' %(sourceId,config['ad']) ,True,[header]))
    last = None
    for source in a['sources']:
        protocol = "dash+xml"
        https = "https"
        #protocol = "x-mpegURL"
        if protocol in source['type']:
            if https in source['vmap']:
                last = source['src']
    return last


def getBrightcoveConfig():
    # hardcoded, in case...
    answer = {}
    answer['key'] = 'BCpkADawqM3lBz07fdV6Q__Z8jM6RenArMfaM8YoxyIBexztP2lLBvXw2PlknyXbnK_1MMSmXw7qKqOM9mPI-doKvmqeywTJ3wKVzhdJSQN8JthhhmrUT5zVikMU8OvQEGirR-e7e7iqmZSC'
    answer['ad'] = 'dcd6de5f-a864-4ef6-b416-dcdc4f4af216'
    try:
        data = cache.get_cached_content('https://players.brightcove.net/6150020952001/default_default/config.json',True)
        jsonData =  json.loads(data)
        answer['key']  =jsonData['video_cloud']['policy_key']
        answer['ad'] = jsonData['ad_config_id']

    except Exception:
        log.log('ERREUR, impossible de récupérer dynamiquement la configuration de Brightcove.')
 
    return answer



def remove_any_html_tags(text, crlf=True):
    """ function docstring """
    try:
        text = RE_HTML_TAGS.sub('', text)
        text = text.lstrip()
        if crlf == True:
            text = RE_AFTER_CR.sub('', text)
        return text
    except Exception:
        return ''

def obtenirMeilleurStream(pl,word='http'):
    maxBW = 0
    bandWidth=None
    uri = None
    res = None
    maxres = int(ADDON.getSetting("MaxResolution"))

    for line in pl.split('\n'):
        if re.search('#EXT-X',line):
            bandWidth = None
            try:
                match = re.search(r'BANDWIDTH=(\d+)',line)
                bandWidth = int(match.group(1))
                log.log('LE courant bandwitdh vaut %s' % bandWidth)
            except :
                bandWidth = None
            res = None
            try:
                match = re.search(r'RESOLUTION=\d+x(\d+)',line)
                res = int(match.group(1))
                log.log('LE résolution courante vaut %s' % res)
            except :
                res = None
        elif line.startswith(word):
            if bandWidth != None:
                if bandWidth > maxBW:
                    if res != None and res <= maxres:
                        maxBW = bandWidth
                        uri = line
    log('LE BITRATE CHOISI EST ________%s' % maxBW)
    return uri
