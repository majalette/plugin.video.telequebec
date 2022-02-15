# -*- coding: utf-8 -*-
# version 3.2.2 - By dualB

import sys, re
import xbmcaddon
from . import cache, html, log, parse

try:
    import json
except ImportError:
    import simplejson as json

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import unquote, quote_plus, unquote_plus, urljoin, urlparse
    from urllib.request import Request, urlopen
else:
    # Python 2 stuff
    from urlparse import urljoin, urlparse
    from urllib import quote_plus, unquote_plus, unquote
    from urllib2 import Request, urlopen


# Nouveau site de TQ
# Account id : 6101674910001
# Policy Key : BCpkADawqM2i8RZms9AMLB7fASCDVh6nXbM3w8f53CuvNwHk2vWwoJ-JjQUQ6e-rizFEiBj9FCldU7jMYNsViVF2-0I2EMUAAaRtGPzD1RLAco3K6aQaEUjfaR-BB0b3X-ARQ3v9-MQSg_bt

# Episode de robocar poli
# video id : 6211205520001

SUR_DEMANDE = 'https://beacon.playback.api.brightcove.com/telequebec/api/menus/0/option/29060-sur-demande?device_type=web&device_layout=web'

BASE_URL = 'http://zonevideo.api.telequebec.tv/data/v2/[YourApiKey]/'
AZ_URL = 'http://zonevideo.api.telequebec.tv/data/v2/[YourApiKey]/Az'
DOSSIERS_URL = 'http://zonevideo.api.telequebec.tv/data/v2/[YourApiKey]/folders'
POPULAIRE_URL = 'http://zonevideo.api.telequebec.tv/data/v2/[YourApiKey]/populars/'

MEDIA_BUNDLE_URL = BASE_URL + 'MediaBundle/'

SEASON = 'Saison'
EPISODE = 'Episode'
LABEL = 'label'
FILTRES = '{"content":{"genreId":"","mediaBundleId":-1},"show":{"' + SEASON + '":"","' + EPISODE + '":"","' + LABEL + '":""},"fullNameItems":[],"sourceId":""}'
INTEGRAL = 'Integral'

def getCategories():
    liste = []
    raw = json.loads(cache.get_cached_content(SUR_DEMANDE))
    
    blocks = raw['data']['screen']['blocks']
    for block in blocks :
        liste.append({'name' : block['widgets'][0]['name'], 'playlist_url' : block['widgets'][0]['playlist']['playlist_ref']})
    return liste

def dictOfGenres(filtres):
    liste =[]
    liste.append({'genreId': 0, 'nom': 'Coucou','resume':'La section jeunesse de TQ'})
    liste.append({'genreId': 1, 'nom': 'Documentaires','resume':'Les documentaires.'})
    liste.append({'genreId': 2, 'nom': 'Famille', 'resume':'Pour toute la famille.'})
    liste.append({'genreId': 3, 'nom': 'Films','resume':'Les films.'})
    liste.append({'genreId': 6, 'nom': 'Jeunesse - tout-petits','resume':'Pour les petits.'})
    liste.append({'genreId': 4, 'nom': 'Jeunesse - grands','resume':'Pour les plus grands.'})
    liste.append({'genreId': 5, 'nom': 'Jeunesse - plus grands','resume':'Pour les vraiment grands.'})
    liste.append({'genreId': 7, 'nom': 'Magazines','resume':'Les magasines.'})
    liste.append({'genreId': 9, 'nom': 'S%C3%A9ries de fiction','resume':'La fiction.'})
    liste.append({'genreId': 10, 'nom': 'Vari%C3%A9t%C3%A9s','resume':'Pour se divertir.'})

    for item in liste :
        item['isDir']= True
        item['nom']= unquote(item['nom'])
        item['url'] = AZ_URL
        item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']

    return liste

def dictOfMainDirs(filtres):
    liste = []

    liste.append({'genreId': -2, 'nom': '[B]Populaires[/B]', 'url' : POPULAIRE_URL,'resume':'Les videos populaires du moment.'})
    liste.append({'genreId': -1, 'nom': '[B]Dossiers[/B]', 'url': DOSSIERS_URL,'resume':'Des segments abordant un sujet commun.'})

    for item in liste :
        item['isDir']= True
        item['nom']= unquote(item['nom'])
        item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        item['filtres']= parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        item['filtres']['show']={}
        item['filtres']['fullNameItems'].append('nomDuShow')        
    return liste

def dictOfPopulaires(filtres):
    liste=[{'genreId': -21, 'nom': 'Populaires en ce moment', 'url' : 'Day/','resume':'Les videos populaires en ce moment.'}]
    liste.append({'genreId': -22, 'nom': 'Populaires cette semaine', 'url' :'Week/','resume':'Les videos populaires cette semaine.'})
    liste.append({'genreId': -23, 'nom': 'Populaires depuis 1 mois', 'url' : 'Month/','resume':'Les videos populaires depuis 1 mois.'})
    for item in liste :
        item['isDir']= True
        item['nom']= unquote(item['nom'])
        item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        item['filtres']= parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        item['filtres']['content']['url'] = item['url']
        item['filtres']['show']={}
        item['filtres']['fullNameItems'].append('nomDuShow')        
    return liste

    
def formatListe(liste, filtres):
    newListe = []
    for item in liste:
        newItem = {}
        newItem['isDir'] = True
        newItem['nom'] = item['view']['title']
        newItem['mediaBundleId'] = item['mediaBundleId']
        newItem['url'] = MEDIA_BUNDLE_URL + str(item['mediaBundleId'])
        newItem['image'] = getThumbnails(item)
        newItem['genreId'] = ''
        newItem['nomComplet'] = item['view']['title']
        newItem['resume'] = item['view']['description']
        newItem['fanart'] = getFanArt(item)
        newItem['filtres'] = parse.getCopy(filtres)
        newItem['filtres']['content']['mediaBundleId'] = item['mediaBundleId']
        newListe.append(newItem)
    return newListe

def get_liste_populaire(filtres):
    show = getLinkPop(filtres['content']['url'])
    items = show['items']

    newListe = []
    for episode in items:
        newItem = {}
        newItem['isDir'] = False
        newItem[LABEL] = 'Contenu'
        newItem['categoryType'] = episode['categoryType']
        newItem['url'] = episode['permalink']
        newItem['image'] = getThumbnails(episode)
        newItem['genreId'] = ''
        newItem['nomComplet'] = episode['view']['title']
        newItem['resume'] = episode['view']['description']

        try:
             newItem[SEASON] = episode['view']['season'].encode('utf-8','ignore')
        except Exception:
             newItem[SEASON] =''
        
        newItem['duree'] = episode['duration']/1000
        newItem['seasonNo'] = newItem[SEASON]
        
        try:
            newItem['episodeNo'] =episode['view']['episode'].encode('utf-8','ignore')
        except Exception:
            newItem['episodeNo'] =''
            
        newItem['startDate'] = episode['startDate']
        newItem['endDate'] = episode['endDate']
        newItem['endDateTxt'] = episode['view']['endDate']


        newItem['streamInfo'] = episode['streamInfo']

        newItem['nomDuShow'] =  episode['view']['containerTitle']
        
        newItem['sourceId'] = episode['streamInfo']['sourceId']
        newItem[EPISODE] = str(newItem['episodeNo'])
        newItem['fanart'] = getImage(episode['view']['thumbImg'],'1280','720')
        newItem['nom'] = ''

        newItem['nom'] = episode['view']['containerTitle'] + ' - ' + episode['view']['title']
        newListe.append(newItem)

    return newListe
    
def getListeOfVideo(mediaBundleId, filtres):
    show = getShow(mediaBundleId)
    fanart_url = getFanArt(show)
    mainShowName = show['view']['title']
    
    newListe = []
    for bloc in show['mediaGroups']:
        if bloc['label'] == None:
            nomBloc = 'Contenu'
        else:
            nomBloc = bloc['label']
        
        for episode in bloc['medias']:
            newItem = {}
            newItem['isDir'] = False
            newItem[LABEL] = nomBloc
            newItem['categoryType'] = episode['categoryType']
            newItem['url'] = episode['permalink']
            newItem['image'] = getThumbnails(episode)
            newItem['genreId'] = ''
            newItem['nomComplet'] = episode['view']['title']
            newItem['resume'] = episode['view']['description']
            newItem[SEASON] = 'Saison ' + str(episode['seasonNo'])
            newItem['duree'] = episode['duration']/1000

            
            newItem['seasonNo'] = episode['seasonNo']
            newItem['episodeNo'] =episode['episodeNo']
            newItem['startDate'] = episode['startDate']
            newItem['endDate'] = episode['endDate']
            newItem['endDateTxt'] = episode['view']['endDate']


            newItem['streamInfo'] = episode['streamInfo']

            newItem['nomDuShow'] = mainShowName
            
 
            newItem['sourceId'] = episode['streamInfo']['sourceId']
            newItem[EPISODE] = 'Episode ' + str(episode['episodeNo']).zfill(2)
            newItem['fanart'] = fanart_url
            newItem['nom'] = ''

            for tag in filtres['fullNameItems']:
                newItem['nom'] = newItem['nom'] + newItem[tag] + ' - '


            newItem['nom'] = newItem['nom'] + episode['view']['title']
            newListe.append(newItem)

    return newListe

def get_liste_emissions(filtres):
    liste = get_liste(filtres['content']['genreId'])
    return formatListe(liste, filtres)

def get_liste(categorie):
    if categorie >= 0:
        liste = getJsonBlock(AZ_URL, 0)
        if categorie == 0:
            return liste
        listeFiltree = []
        for show in liste:
            if isGenre(categorie, show):
                listeFiltree.append(show)

        return listeFiltree
    if categorie == -1:
        return getJsonBlock(DOSSIERS_URL, 1)
    if categorie == -2:
        return getJsonBlock(POPULAIRE_DAY,1)['data'][0]['items']
    return {}

def isGenre(genreValue, show):
    genres = show['genres']
    for genre in genres:
        if genre['genreId'] == genreValue:
            return True

    return False

def isIntegral(show):
    if show['categoryType']==INTEGRAL:
        return True
    else:
        return False

def getThumbnails(show):
    return getImage(show['view']['thumbImg'], '320','180')

def getFanArt(show):
    return getImage(show['view']['headerImg'],'1600','900')

def getImage(url,width,height):
    link = re.sub('{w}', width, url)
    link = re.sub('{h}', height, link)
    return link
    
def getShow(mediaBundleId):
    database = json.loads(cache.get_cached_content(MEDIA_BUNDLE_URL + str(mediaBundleId)))
    return database['data']

def getLinkPop(url):
    
    database = json.loads(cache.get_cached_content(POPULAIRE_URL + str(url)))
    return database['data'][0]

def getJsonBlock(url, block):
    dataBlock = []
    try:
        db = json.loads(cache.get_cached_content(url))
        dataBlock = db['data'][block]['items']
    except Exception:
        dataBlock = []
    return dataBlock


