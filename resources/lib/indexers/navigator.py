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

    def root(self):
        self.addDirectoryItem("Videótár", "videok_items", '', 'DefaultFolder.png')
        self.addDirectoryItem("Legfrissebb videók", "friss_items", '', 'DefaultFolder.png')
        self.addDirectoryItem("Élő közvetítések", "live_items", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "newsearch", '', 'DefaultFolder.png')
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

            self.addDirectoryItem(f'[B]{main_title}[/B]', f'get_vods&url={fix_videok_link}&arena4_online_session_value={arena4_online_session_value}&main_title={main_title}', main_img_url, 'DefaultMovies.png', isFolder=True, meta={'title': main_title})

        self.endDirectory()

    def getFrssVideok(self):
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
        
        cookies_2 = {
            '__e_inc': '1',
            'arena4_online_session': arena4_online_session_value,
        }
        
        headers_2 = {
            'authority': 'arena4plus.network4.hu',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }        
        
        
        response_2 = requests.get(f"{base_url}/collections/legfrissebb-videok", headers=headers_2, cookies=cookies_2)
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
                'id': finger_id,
                'name': 'collection-items',
                'locale': 'hu',
                'path': 'collections/legfrissebb-videok',
                'method': 'GET',
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': html_Hash,
                'data': {
                    'textcolor': 'text--white',
                    'collection_id': 8,
                    'collection_type': 'latest-videos',
                    'items': 1000,
                    'videoid': '',
                    'type': 'collectionsview',
                    'grouptype': 'latest-videos',
                    'readyToLoad': False,
                },
                'dataMeta': [],
                'checksum': check_sum,
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
            link_url = item.find('a', {'class': 'ratio--16-9'})['href']
            fix_videok_link = f'{base_url}{link_url}'
            
            image_url = item.find('a', {'class': 'ratio--16-9'}).get('style').split('url(')[2].split(')')[0].strip("'")
            
            locked_or_not = re.findall(r'net4plus_(.*).png', str(item))[0].strip()
            
            category_title_elem = item.find('div', {'class': 'text-white bg-green text-black pr-1 pl-1 font-bold'})
            category_title = category_title_elem.text.strip() if category_title_elem else None
            
            title_elem = item.find('h3', {'class': 'head-2'})
            title_part1 = title_elem.text.strip() if title_elem else None
        
            title_part2_elem = item.find('div', {'class': 'pl-2 pr-2 lg:pl-0 lg:pr-0 xl:text-lg text-white'})
            title_part2 = title_part2_elem.text.strip() if title_part2_elem else None
        
            main_title = f"{title_part1} {title_part2}" if title_part2 else title_part1
            
            if re.search(r'lakat', locked_or_not):
                self.addDirectoryItem(f'[B][COLOR red]| {category_title} | {main_title}[/COLOR][/B]', f'get_mpd_lic&url={fix_videok_link}&arena4_online_session_value={arena4_online_session_value}&image_url={image_url}&main_title={main_title}', image_url, 'DefaultMovies.png', isFolder=True, meta={'title': main_title})
            else:
                self.addDirectoryItem(f'[B] {category_title} | {main_title}[/B]', f'get_mpd_lic&url={fix_videok_link}&arena4_online_session_value={arena4_online_session_value}&image_url={image_url}&main_title={main_title}', image_url, 'DefaultMovies.png', isFolder=True, meta={'title': main_title})     

        self.endDirectory()

    def getLiveVideok(self):
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
        
        cookies_2 = {
            '__e_inc': '1',
            'arena4_online_session': arena4_online_session_value,
        }
        
        headers_2 = {
            'authority': 'arena4plus.network4.hu',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }        

        response_2 = requests.get(f"{base_url}/collections/live/collection", headers=headers_2, cookies=cookies_2)
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
                'name': 'collection-items',
                'locale': 'hu',
                'path': 'collections/live/collection',
                'method': 'GET',
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': f'{html_Hash}',
                'data': {
                    'textcolor': 'text--white',
                    'collection_id': 7,
                    'collection_type': 'live',
                    'items': 1000,
                    'videoid': '',
                    'type': 'collectionsview',
                    'grouptype': 'live',
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
        
        for item in soup_x.find_all('div', attrs={'data-component': 'item'}):
            live_url_elem = item.find('a', {'data-collection': 'Y'})
            live_url = live_url_elem.get('href').strip() if live_url_elem else ''
        
            fix_videok_link = f'{base_url}{live_url}'
        
            image_style = item.select_one('a[data-collection="Y"]').get('style')
            background_images = re.findall(r"url\(\'(.*?)\'\)", image_style)
            image_url = background_images[-1] if background_images else ''
        
            category_title_elem = item.find('div', class_='text-white bg-green text-black pr-1 pl-1 font-bold')
            category_title = category_title_elem.text.strip() if category_title_elem else ''
        
            main_title_elem = item.find('h3', class_='head-2')
            main_title = main_title_elem.text.strip() if main_title_elem else ''

            additional_title_elem = item.find('div', class_='pl-2 pr-2 lg:pl-0 lg:pr-0 xl:text-lg text-white')
            additional_title = additional_title_elem.text.strip() if additional_title_elem else ''

            if additional_title:
                main_title = f"{main_title} {additional_title}"
        
            live_pulse_elem = item.find('span', class_='animate-pulse')
            live_pulse = live_pulse_elem.text.strip() if live_pulse_elem else ''
            
            if live_pulse == 'ÉLŐ':
                self.addDirectoryItem(f'[B]| {live_pulse} | {category_title} | {main_title}[/B]', f'get_live_mpd_lic&url={fix_videok_link}&arena4_online_session_value={arena4_online_session_value}&image_url={image_url}&main_title={main_title}&category_title={category_title}', image_url, 'DefaultMovies.png', isFolder=True, meta={'title': main_title})
        
        self.endDirectory()    

    def getVods(self, url, arena4_online_session_value, both_title, image_url, main_title):
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
            main_cat = item.find('div', {'class': 'text-white bg-green text-black pr-1 pl-1 font-bold'}).text.strip()
            title_part_1 = item.find('h3', {'class': 'pl-2 pr-2 lg:pr-0 lg:pl-0 head-2 mt-4 md:mt-0 lg:mt-4 text-white'}).text.strip()
            title_part_2 = item.find('div', {'class': 'pl-2 pr-2 lg:pl-0 lg:pr-0 xl:text-lg text-white'}).text.strip()

            both_title = f'{title_part_1} / {title_part_2}'

            locked_or_not = re.findall(r'net4plus_(.*).png', str(item))[0].strip()
            
            if re.search(r'lakat', locked_or_not):
                self.addDirectoryItem(f'[B][COLOR red]{both_title}[/COLOR][/B]', f'get_mpd_lic&url={url_vod}&arena4_online_session_value={arena4_online_session_value}&both_title={both_title}&image_url={image_url}&main_title={main_title}', image_url, 'DefaultMovies.png', isFolder=True, meta={'title': both_title})
            else:    
                self.addDirectoryItem(f'[B]{both_title}[/B]', f'get_mpd_lic&url={url_vod}&arena4_online_session_value={arena4_online_session_value}&both_title={both_title}&image_url={image_url}&main_title={main_title}', image_url, 'DefaultMovies.png', isFolder=True, meta={'title': both_title})

        self.endDirectory()

    def getMpdLic(self, url, arena4_online_session_value, both_title, image_url, main_title):
        
        try:
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
            
            cookies_2 = {
                '__e_inc': '1',
                'arena4_online_session': arena4_online_session_value,
            }
            
            headers_2 = {
                'authority': 'arena4plus.network4.hu',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            }
            
            response_2 = requests.get(f"{url}", headers=headers_2, cookies=cookies_2).text
            stream_url = re.findall(r'src\":\"(https://.*mpd.*)\"', response_2)[0].strip()
            
            response_3 = requests.get(stream_url).text
            lic_url = re.findall(r'license[uU]rl=\"(.*?)\"', response_3)[0].strip()
            
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getMpdLic | both_title | {both_title}', xbmc.LOGINFO)
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getMpdLic | stream_url | {stream_url}', xbmc.LOGINFO)

            if re.search(r'None', str(both_title)):
                full_title = f'{main_title}'
                both_title = f'{main_title}'
            else:
                full_title = f'{main_title}\n{both_title}'

            lic = lic_url + '||R{SSM}|'
            
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getMpdLic | lic | {lic}', xbmc.LOGINFO)
            
            list_item = xbmcgui.ListItem(path=stream_url)

            list_item.setInfo('video', {'title': both_title, 'plot': full_title})
            list_item.setArt({'poster': image_url})
            
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            list_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            list_item.setProperty('inputstream.adaptive.license_key', lic)
            
            xbmc.Player().play(stream_url, list_item)

        except IndexError:
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getMpdLic | lezárt tartalom/session probléma', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("Arena4Plus", "lezárt tartalom / session probléma", time=5000)        

    def getLiveMpdLic(self, url, arena4_online_session_value, both_title, image_url, main_title, category_title):
        
        try:
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
            
            #for live need the second mpd link from the first mpd url
            stream = re.findall(r'src\":\"(https://.*mpd.*)\"', str(soup_xx))[0].strip()
            
            response_3 = requests.get(stream)
            soup_lic = BeautifulSoup(response_3.text, 'html.parser')
            
            lic_url = re.findall(r'licenseurl=\"(.*?)\"', str(soup_lic))[0].strip()
            stream_url = re.findall(r'<location>(.*)</location>', str(soup_lic))[0].strip()
            
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            lic = lic_url + '|User-Agent=' + user_agent + '&Referer=' + base_url +'/&Origin=' + base_url + '&Content-Type= |R{SSM}|'
            
            list_item = xbmcgui.ListItem(path=stream_url)
            
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            list_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            list_item.setProperty('inputstream.adaptive.license_key', lic)
            
            if re.search(r'None', str(both_title)):
                full_title = f'| {category_title} | {main_title}'
                both_title = f'| {category_title} | {main_title}'
            else:
                full_title = f'{main_title}\n{both_title}'
            
            list_item.setInfo('video', {'title': both_title, 'plot': full_title})
            list_item.setArt({'poster': image_url})
            
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getLiveMpdLic | both_title | {both_title}', xbmc.LOGINFO)
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getLiveMpdLic | stream_url | {stream_url}', xbmc.LOGINFO)
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getLiveMpdLic | lic_url | {lic_url}', xbmc.LOGINFO)
            
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getLiveMpdLic | inputstream.adaptive.license_key | {lic}', xbmc.LOGINFO)
            
            xbmc.Player().play(stream_url, list_item)
        except IndexError:
            xbmc.log(f'Arena4Plus | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getLiveMpdLic | lezárt tartalom/session probléma', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("Arena4Plus", "lezárt tartalom / session probléma", time=5000)

    def doSearch(self, url):
        search_text = self.getSearchText()
        
        notification = xbmcgui.Dialog()
        notification.notification("Arena4Plus", f"Keresés: {search_text} folyamatban...", time=5000)        

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
        
        cookies_2 = {
            '__e_inc': '1',
            'arena4_online_session': arena4_online_session_value,
        }
        
        headers_2 = {
            'authority': 'arena4plus.network4.hu',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }        
        
        
        response_2 = requests.get(f"{base_url}/search", headers=headers_2, cookies=cookies_2)
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
                'name': 'search',
                'locale': 'hu',
                'path': 'search',
                'method': 'GET',
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': f'{html_Hash}',
                'data': {
                    'search': '',
                    'videos': [],
                    'articles': [],
                    'leadingarticles': [],
                    'opinionarticles': [],
                    'podcasts': [],
                    'searchphrase': None,
                    'type': 'full',
                },
                'dataMeta': [],
                'checksum': f'{check_sum}',
            },
            'updates': [
                {
                    'type': 'syncInput',
                    'payload': {
                        'name': 'search',
                        'value': f'{search_text}',
                    },
                },
            ],
        }
        
        
        response_x = requests.post('https://arena4plus.network4.hu/livewire/message/collection-items', cookies=cookies_x, headers=headers_x, json=json_data_x).json()
        
        effects_data = response_x.get('effects', {})
        html_content = effects_data.get('html', '')
        soup_x = BeautifulSoup(html_content, 'html.parser')
        
        video_blocks = soup_x.find_all('div', class_='md:flex lg:block')
        
        for block in video_blocks:
        
            link_url = block.find('a')['href']
            fix_videok_link = f'{base_url}{link_url}'

            # category_element = block.find('div', class_='bg-green')
            # category_title = category_element.text.strip() if category_element else "Category Not Found"
            
            title_1 = block.find('h3').text.strip()
            title_2 = block.find('div', class_='xl:text-lg').text.strip()

            style_attr = block.find('a')['style']
            image_url = re.findall(r"url\('(http.?.*)'", str(style_attr))[0].strip()
            
            both_title = f'{title_1} / {title_2}'

            self.addDirectoryItem(both_title, f'get_mpd_lic&url={fix_videok_link}&both_title={both_title}&image_url={image_url}', image_url, 'DefaultFolder.png')
        
        self.endDirectory()

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