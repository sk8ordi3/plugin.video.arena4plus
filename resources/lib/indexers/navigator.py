# -*- coding: utf-8 -*-

'''
    Arena4Plus Addon
    Copyright (C) 2023 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
import urllib.parse
import resolveurl as urlresolver
from resources.lib.modules.utils import py2_decode, py2_encode
import html

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

import platform
import xml.etree.ElementTree as ET

os_info = platform.platform()
kodi_version = xbmc.getInfoLabel('System.BuildVersion')

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_directory)))
addon_xml_path = os.path.join(parent_directory, "addon.xml")

tree = ET.parse(addon_xml_path)
root = tree.getroot()
version = root.attrib.get("version")

xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info}', xbmc.LOGINFO)

addon = xbmcaddon.Addon('plugin.video.arena4plus')
user_name = addon.getSetting('username')
pass_word = addon.getSetting('password')

if not user_name or not pass_word:
    xbmc.log("Username or password not set, opening settings", level=xbmc.LOGINFO)
    addon.openSettings()

base_url = 'https://arena4plus.network4.hu'

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):       
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))
        self.searchFileName = os.path.join(self.base_path, "search.history")        

    def root(self):
        self.addDirectoryItem("Videók", "videok_items", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "search", '', 'DefaultFolder.png')
        self.endDirectory()
        
    def getVideok(self):
        import requests
        import json
        import re
        
        login_url = "https://arena4plus.network4.hu/login"
        
        headers = {
            'authority': 'arena4plus.network4.hu',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://arena4plus.network4.hu',
            'referer': 'https://arena4plus.network4.hu/login',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }

        response = requests.get(login_url)
        token = re.findall(r'<meta name="csrf-token" content="([^"]*)">', response.text)[0]

        data = {
            '_token': token,
            'email': user_name,
            'password': pass_word,
        }

        cookies = response.cookies
        
        response = requests.post(login_url, headers=headers, cookies=cookies, data=data)

        cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
        arena4_online_session_value = cookies_dict.get('arena4_online_session', None)
        
        xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | arena4_online_session_value | {arena4_online_session_value}', xbmc.LOGINFO)
        
        cookies_2 = {
            '__e_inc': '1',
            'arena4_online_session': arena4_online_session_value,
        }
        
        headers_2 = {
            'authority': 'arena4plus.network4.hu',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }        
        
        
        response_2 = requests.get(f"{base_url}/collections", headers=headers_2, cookies=cookies_2)
        soup = BeautifulSoup(response_2.text, 'html.parser')
        
        csrf = re.findall(r'<meta content=\"(.*)\" name=\"csrf-token\"/>', str(soup))[0].strip()
        
        coll_items = re.findall(r"wire:initial-data='(.*)'", str(soup))[0].strip()
        decoded_html = html.unescape(coll_items)
        decoded_html = json.loads(decoded_html)
        
        finger_id = decoded_html['fingerprint']['id']
        html_Hash = decoded_html['serverMemo']['htmlHash']
        check_sum = decoded_html['serverMemo']['checksum']
        
        cookies_x = {
            'arena4_online_session': f'{arena4_online_session_value}',
        }
        
        headers_x = {
            'authority': 'arena4plus.network4.hu',
            'accept': 'text/html, application/xhtml+xml',
            'accept-language': 'hu,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://arena4plus.network4.hu',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'x-csrf-token': f'{csrf}',
            'x-livewire': 'true',
        }
        
        json_data_x = {
            'fingerprint': {
                'id': f'{finger_id}',
                'name': 'collections',
                'locale': 'hu',
                'path': 'collections',
                'method': 'GET',
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': f'{html_Hash}',
                'data': {
                    'collection_id': '',
                    'collection_type': '',
                    'items': '',
                    'type': 'modal',
                    'readyToLoad': False,
                    'collectionsmodalOpen': True,
                },
                'dataMeta': [],
                'checksum': f'{check_sum}',
            },
            'updates': [
                {
                    'type': 'callMethod',
                    'payload': {
                        'method': 'loadItems',
                        'params': [],
                    },
                },
            ],
        }
        

        response_x = requests.post('https://arena4plus.network4.hu/livewire/message/collection-items', cookies=cookies_x, headers=headers_x, json=json_data_x).json()

        effects_data = response_x.get('effects', {})
        html_content = effects_data.get('html', '')
        soup_x = BeautifulSoup(html_content, 'html.parser')
        
        main_blocks = soup_x.find_all('div', class_='flex sm:flex xl:flex-item xl:block w-full xl:p-8 xl:w-3/12 focus:ring-2 focus:ring-white focus:shadow-2xl navigable focus:scale-110 hover:scale-105 transform')
        
        for block in main_blocks:
            main_link_id = block.find('a', href=True)['href']
            fix_videok_link = f'{base_url}{main_link_id}'

            main_img_url = block.find('img')['src']
            
            main_title_divs = block.find_all('div', class_='text-white')
            main_title_parts = [div.text.strip() for div in main_title_divs]
            
            main_title = ' '.join(main_title_parts)

            self.addDirectoryItem(f'[B]{main_title}[/B]', f'get_vods&url={fix_videok_link}&arena4_online_session_value={arena4_online_session_value}', main_img_url, 'DefaultMovies.png', isFolder=True, meta={'title': main_title})

        self.endDirectory()

    def getVods(self, url, arena4_online_session_value, both_title):
        import requests
        import json
        import re
        
        cookies_2 = {
            '__e_inc': '1',
            'arena4_online_session': arena4_online_session_value,
        }
        
        headers_2 = {
            'authority': 'arena4plus.network4.hu',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }

        response_2 = requests.get(f"{url}", headers=headers_2, cookies=cookies_2)
        soup = BeautifulSoup(response_2.text, 'html.parser')
        
        url_id = re.findall(r'.hu/(.*)', url)[0].strip()
        
        csrf = re.findall(r'<meta content=\"(.*)\" name=\"csrf-token\"/>', str(soup))[0].strip()
        
        coll_items = re.findall(r"initial-data=.(.*normal.*}})", str(soup))[0].strip()
        decoded_html = html.unescape(coll_items)
        decoded_html = json.loads(decoded_html)
        
        finger_id = decoded_html['fingerprint']['id']
        html_Hash = decoded_html['serverMemo']['htmlHash']
        check_sum = decoded_html['serverMemo']['checksum']
        coll_id = decoded_html['serverMemo']['data']['collection_id']
        
        xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getVods | url | {url}', xbmc.LOGINFO)
        xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getVods | url_id | {url_id}', xbmc.LOGINFO)
        xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getVods | csrf | {csrf}', xbmc.LOGINFO)
        xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getVods | finger_id | {finger_id}', xbmc.LOGINFO)
        xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getVods | html_Hash | {html_Hash}', xbmc.LOGINFO)
        xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getVods | check_sum | {check_sum}', xbmc.LOGINFO)
        xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getVods | coll_id | {coll_id}', xbmc.LOGINFO)
        
        cookies_x = {
            'arena4_online_session': f'{arena4_online_session_value}',
        }
        
        headers_x = {
            'authority': 'arena4plus.network4.hu',
            'accept': 'text/html, application/xhtml+xml',
            'accept-language': 'hu,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://arena4plus.network4.hu',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'x-csrf-token': f'{csrf}',
            'x-livewire': 'true',
        }
        
        json_data_x = {
            'fingerprint': {
                'id': f'{finger_id}',
                'name': 'collection-items',
                'locale': 'hu',
                'path': f'{url_id}',
                'method': 'GET',
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': f'{html_Hash}',
                'data': {
                    'textcolor': 'text--white',
                    'collection_id': int(coll_id),
                    'collection_type': 'collection',
                    'items': 1000,
                    'videoid': '',
                    'type': 'collectionsview',
                    'grouptype': 'normal',
                    'readyToLoad': False,
                },
                'dataMeta': [],
                'checksum': f'{check_sum}',
            },
            'updates': [
                {
                    'type': 'callMethod',
                    'payload': {
                        'method': 'loadItems',
                        'params': [],
                    },
                },
            ],
        }

        response_x = requests.post('https://arena4plus.network4.hu/livewire/message/collection-items', cookies=cookies_x, headers=headers_x, json=json_data_x).json()

        effects_data = response_x.get('effects', {})
        html_content = effects_data.get('html', '')
        soup_x = BeautifulSoup(html_content, 'html.parser')
        
        items = soup_x.find_all('div', {'data-component': 'item'})
        
        for item in items:
            url = item.find('a')['href']
            url_vod = f'{base_url}{url}'
            
            image_url = item.find('a')['style'].split('url(')[2].split(')')[0].strip("'")
            main_title = item.find('div', {'class': 'text-white bg-green text-black pr-1 pl-1 font-bold'}).text.strip()
            title_part_1 = item.find('h3', {'class': 'pl-2 pr-2 lg:pr-0 lg:pl-0 head-2 mt-4 md:mt-0 lg:mt-4 text-white'}).text.strip()
            title_part_2 = item.find('div', {'class': 'pl-2 pr-2 lg:pl-0 lg:pr-0 xl:text-lg text-white'}).text.strip()

            both_title = f'{title_part_1} {title_part_2}'

            self.addDirectoryItem(f'[B]{both_title}[/B]', f'get_mpd_lic&url={url_vod}&arena4_online_session_value={arena4_online_session_value}&both_title={both_title}', image_url, 'DefaultMovies.png', isFolder=True, meta={'title': both_title})

        self.endDirectory()

    def getMpdLic(self, url, arena4_online_session_value, both_title):
        import requests
        import re
        
        cookies_2 = {
            '__e_inc': '1',
            'arena4_online_session': arena4_online_session_value,
        }
        
        headers_2 = {
            'authority': 'arena4plus.network4.hu',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }

        response_2 = requests.get(f"{url}", headers=headers_2, cookies=cookies_2)
        soup_xx = BeautifulSoup(response_2.text, 'html.parser')        
        
        get_mpd = re.findall(r'src\":\"(https://.*mpd.*)\"', str(soup_xx))[0].strip()
        print(f'\n{get_mpd}\n')
        
        xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getVods | both_title | {both_title}', xbmc.LOGINFO)
        xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getVods | get_mpd | {get_mpd}', xbmc.LOGINFO)
        
        self.endDirectory()

    def playMovie(self, url):
        page = requests.get(url, headers=headers)
        parsed_uri = urlparse(page.url)
        soup = BeautifulSoup(page.text, 'html.parser')
        captions = soup.find_all('track', attrs={"kind": "captions"})
        subtitles = []
        for caption in captions:
            subtitles.append({"language": caption["srclang"], "url": f'{parsed_uri.scheme}://{parsed_uri.netloc}{caption["src"]}'})
        try:
            direct_url = urlresolver.resolve(url)
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | playMovie | direct_url: {direct_url}', xbmc.LOGINFO)
            play_item = xbmcgui.ListItem(path=direct_url)
            if 'm3u8' in direct_url:
                from inputstreamhelper import Helper
                is_helper = Helper('hls')
                if is_helper.check_inputstream():
                    play_item.setProperty('inputstream', 'inputstream.adaptive')  # compatible with recent builds Kodi 19 API
                    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            if len(subtitles) > 0:
                errMsg = ""
                try:
                    if not os.path.exists(self.base_path):
                        errMsg = "Hiba a kiegészítő userdata könyvtár létrehozásakor"
                        os.mkdir(self.base_path)
                    if not os.path.exists(os.path.join(self.base_path, 'subtitles')):
                        errMsg = "Hiba a felirat könyvtár létrehozásakor!"
                        os.mkdir(os.path.join(self.base_path, 'subtitles'))
                    for f in os.listdir(os.path.join(self.base_path, 'subtitles')):
                        errMsg = "Hiba a korábbi feliratok törlésekor!"
                        os.remove(os.path.join(self.base_path, 'subtitles', f))
                    subtitleFiles = []
                    for subtitle in subtitles:
                        errMsg = "Hiba a felirat fájl letöltésekor!"
                        subtitlePage = requests.get(subtitle["url"])
                        if subtitlePage.ok and len(subtitlePage.content) > 0:
                            errMsg = "Hiba a felirat fájl mentésekor!"
                            file =  open(os.path.join(self.base_path, 'subtitles', f'{subtitle["language"]}.vtt'), "wb")
                            file.write(subtitlePage.content)
                            file.close()
                            subtitleFiles.append(os.path.join(self.base_path, 'subtitles', f'{subtitle["language"]}.vtt'))
                        else:
                            raise
                    if len(subtitleFiles) > 0:
                        errMsg = "Hiba a feliratok beállításakor!"
                        play_item.setSubtitles(subtitleFiles)
                except:
                    xbmcgui.Dialog().notification("Arena4Plus", errMsg)
            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
        except:
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | playMovie | name: No video sources found', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("Arena4Plus", "Törölt tartalom", time=5000)

    def getSearches(self):
        self.addDirectoryItem('[COLOR lightgreen]Új keresés[/COLOR]', 'newsearch', '', 'DefaultFolder.png')
        try:
            file = open(self.searchFileName, "r")
            olditems = file.read().splitlines()
            file.close()
            items = list(set(olditems))
            items.sort(key=locale.strxfrm)
            if len(items) != len(olditems):
                file = open(self.searchFileName, "w")
                file.write("\n".join(items))
                file.close()
            for item in items:
                url_p = f"{base_url}/search_cat.php?film={item}&type=1"
                enc_url = quote_plus(url_p)                
                self.addDirectoryItem(item, f'items&url={url_p}', '', 'DefaultFolder.png')

            if len(items) > 0:
                self.addDirectoryItem('[COLOR red]Keresési előzmények törlése[/COLOR]', 'deletesearchhistory', '', 'DefaultFolder.png')
        except:
            pass
        self.endDirectory()

    def deleteSearchHistory(self):
        if os.path.exists(self.searchFileName):
            os.remove(self.searchFileName)

    def doSearch(self):
        search_text = self.getSearchText()
        if search_text != '':
            if not os.path.exists(self.base_path):
                os.mkdir(self.base_path)
            file = open(self.searchFileName, "a")
            file.write(f"{search_text}\n")
            file.close()
            url = f"{base_url}/search_cat.php?film={search_text}&type=1"
            self.getItems(url)

    def getSearchText(self):
        search_text = ''
        keyb = xbmc.Keyboard('', u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        keyb.doModal()
        if keyb.isConfirmed():
            search_text = keyb.getText()
        return search_text

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)  