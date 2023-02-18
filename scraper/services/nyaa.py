#import modules
from base import *
from ui.ui_print import *
import releases

name = "nyaa"
session = requests.Session()
params = "&c=1_0&s=seeders&o=desc"
proxy = 'nyaa.si'
sleep = "5"
last = 0

# very much leaning on Otaku, show them some love! https://github.com/Goldenfreddy0703/Otaku/blob/main/plugin.video.otaku/resources/lib/pages/nyaa.py

def setup(cls, new=False):
    from scraper.services import setup
    setup(cls,new)

def get(url):
    global last
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
        if time.time() - last < int(sleep):
            time.sleep(time.time() - last)
        last = time.time()
        response = session.get(url, headers=headers,timeout=60)
        return response
    except:
        return None
def scrape(query, altquery):
    from scraper.services import active
    scraped_releases = []
    if 'nyaa' in active:
        if regex.search(r'(?<=nyaa)(.*?)(?=\))',altquery,regex.I):
            query = '"' + regex.search(r'(?<=nyaa)(.*?)(?=\))',altquery,regex.I).group().replace('.',' ').replace('|','"|"') + '"'
            ui_print("[nyaa] using extended query: " + query,ui_settings.debug)
        if proxy == "":
            proxy = "nyaa.si"
        url = 'https://' + proxy + '/?f=0' + params + '&q=' + str(query) 
        response = None
        try:
            response = get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                pagination_info = soup.find(class_='pagination-page-info')
                text = pagination_info.find(text=True)
                total = regex.search(r'([0-9]+)(?= results)',text,regex.I).group()
                total = int(total)
            except:
                total = 0
            current = -1
            i = 2
            while current < total and i < 5:
                current += 75
                i += 1
                rex = r'(magnet:)+[^"]*'
                list = [
                    {'magnet': i.find('a', {'href': regex.compile(rex)}).get('href'),
                    'name': i.find_all('a', {'class': None})[1].get('title'),
                    'size': i.find_all('td', {'class': 'text-center'})[1].text.replace('i', ''),
                    'seeders': i.find_all('td', {'class': 'text-center'})[3].text}
                    for i in soup.select("tr.danger,tr.default,tr.success")
                ]
                if len(list) > 0:
                    for count, torrent in enumerate(list):
                        title = torrent['name'].strip()
                        title = title.replace(" ", '.')
                        title = regex.sub(r'\.+', ".", title)
                        if regex.match(r'(' + altquery.replace('.', '\.').replace("\.*", ".*") + ')', title,regex.I):
                            download = torrent['magnet']
                            size = torrent['size']
                            seeders = torrent['seeders']
                            if regex.search(r'([0-9]*?\.[0-9])(?= KB)', size, regex.I):
                                size = regex.search(r'([0-9]*?\.[0-9])(?= KB)', size, regex.I).group()
                                size = float(float(size) / 1000 / 1000)
                            elif regex.search(r'([0-9]*?\.[0-9])(?= MB)', size, regex.I):
                                size = regex.search(r'([0-9]*?\.[0-9])(?= MB)', size, regex.I).group()
                                size = float(float(size) / 1000)
                            elif regex.search(r'([0-9]*?\.[0-9])(?= GB)', size, regex.I):
                                size = regex.search(r'([0-9]*?\.[0-9])(?= GB)', size, regex.I).group()
                                size = float(size)
                            else:
                                size = float(size)
                            scraped_releases += [releases.release('[nyaa]', 'torrent', title, [], size, [download], seeders=int(seeders))]
                    response = get(url + '&p=' + str(i))
                    soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            if hasattr(response,"status_code") and not str(response.status_code).startswith("2"):
                ui_print('nyaa error '+str(response.status_code)+': 1337x is temporarily not reachable')
            else:
                ui_print('nyaa error: unknown error')
            response = None
            ui_print('nyaa error: exception: ' + str(e),ui_settings.debug)
    return scraped_releases
