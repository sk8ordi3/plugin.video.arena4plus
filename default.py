# -*- coding: utf-8 -*-

'''
    Arena4Plus Add-on
    Copyright (C) 2020 heg, vargalex

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
import sys
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
url = params.get('url')

arena4_online_session_value = params.get('arena4_online_session_value')
both_title = params.get('both_title')
image_url = params.get('image_url')
main_title = params.get('main_title')
category_title = params.get('category_title')

if action is None:
    navigator.navigator().root()

elif action == 'videok_items':
    navigator.navigator().getVideok()

elif action == 'friss_items':
    navigator.navigator().getFrssVideok()
    
elif action == 'live_items':
    navigator.navigator().getLiveVideok()

elif action == 'get_live_mpd_lic':
    navigator.navigator().getLiveMpdLic(url, arena4_online_session_value, both_title, image_url, main_title, category_title)

elif action == 'get_vods':
    navigator.navigator().getVods(url, arena4_online_session_value, both_title, image_url, main_title)    

elif action == 'get_mpd_lic':
    navigator.navigator().getMpdLic(url, arena4_online_session_value, both_title, image_url, main_title) 

elif action == 'search':
    navigator.navigator().getSearches()

elif action == 'newsearch':
    navigator.navigator().doSearch(url)

elif action == 'deletesearchhistory':
    navigator.navigator().deleteSearchHistory()