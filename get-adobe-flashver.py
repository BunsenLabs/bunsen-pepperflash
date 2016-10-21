#!/usr/bin/env python
#
#    get-adobe-flashver.py: a script to read, from the Adobe website,
#    the version number of the latest flash plugin for a
#    particular OS and browser (Linux, Chromium PPAPI by default).
#
#    Copyright (C) 2016 Jens John <dev@2ion.de>
#    Copyright (C) 2016 John Crawley <john@bunsenlabs.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
from bs4 import BeautifulSoup
import re, sys
try:
    # For Python 3
    from urllib.request import urlopen, URLError
except ImportError:
    # For Python 2
    from urllib2 import urlopen, URLError

# These regexes will be *searched* for in the html table text.
# Use ^ and $ as necessary.
OS_regex = 'Linux'
TYPE_regex = 'Chromium.* PPAPI'

adobe_url = 'https://www.adobe.com/software/flash/about/'
ca_certs_path = '/etc/ssl/certs' # ca-certificates on Debian Jessie

def die(*msgs):
    print(*msgs, sep='\n', file=sys.stderr)
    sys.exit(1)

class Column:
    OS = 0
    TYPE = 1
    VERSION = 2

def table2matrix(t):
    rows = t.find_all("tr")
    m = [ [] for _ in range(len(rows)) ]
    i = 0
    for tr in rows:
        for td in tr.find_all("td"):
            if 'rowspan' in td.attrs:
                rowsp = int(td["rowspan"])
            else:
                rowsp = 1
            for j in range(i, i + int(rowsp)):
                m[j].append(td.get_text(separator=' ', strip=True))
        i += 1
    return [ x for x in m if x ]

def latest_version():
    try:
        body = urlopen(adobe_url, capath=ca_certs_path).read()
        soup = BeautifulSoup(body, 'html.parser')
    except URLError as err:
        die('URLError: Bad URL or certs path?', err)
    except BaseException as err:
        die('Failed to load data', err)
    matrix = table2matrix(soup.find('table', { 'class': 'data-bordered' }))
    version, = [row[Column.VERSION] for row in matrix if re.search(OS_regex, row[Column.OS]) and re.search(TYPE_regex, row[Column.TYPE])]
    return version

if __name__ == '__main__':
    try:
        print(latest_version())
    except ValueError:
        die('Parsing error: regular expressions wrong?')
