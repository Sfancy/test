import sys
import os
import requests
from bs4 import BeautifulSoup
from fileinput import FileInput

payload = {}
headers = {
    'authority': 'www.google.com',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://www.google.com',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': ''
}


def save_m3u8(url, name):
    response = requests.request("GET", url, headers=headers, data=payload)
    with open(name, 'wb') as f:
        f.write(response.content)


def append_baseurl_ts(file_name, base_url):
    if not base_url.endswith('/'):
        base_url = f'{base_url}/'

    with FileInput(file_name, inplace=True) as f:
        for line in f:
            if ".ts" in line:
                print(f'{base_url}{line}', end='\n')
            else:
                print(line, end='')


def parse_video_node(video_node):
    date = ''
    author = ''
    title = ''
    link = ''
    thumb = ''
    duration = ''

    date_node = video_node.select_one(
        'small.text-sub-title div.text-muted + div.text-muted')
    if date_node is not None:
        date = date_node.text.strip().replace(u'\xa0', u'').split('|')[0]

    author_node = video_node.select_one(
        'small.text-sub-title div.text-muted > a.text-dark')
    if author_node is not None:
        author = author_node.text.strip()

    title_node = video_node.select_one('a.title')
    if title_node is not None:
        title = title_node.text.strip()
        link = title_node.get('href').replace(
            '/video/view', 'https://91porny.com/video/embed')

    thumb_node = video_node.select_one('a > div.img')
    if thumb_node is not None:
        thumb = thumb_node.get('style').replace(
            'background-image: url(\'', '').replace('\')', '')

    duration_node = video_node.select_one('a > small.layer')
    if duration_node is not None:
        duration = duration_node.text.strip()

    return {
        'date': date,
        'author': author,
        'title': title,
        'link': link,
        'thumb': thumb,
        'duration': duration,
    }


def start(url):
    response = requests.request("GET", url, headers=headers, data=payload)
    soup = BeautifulSoup(response.content, 'html.parser',
                         from_encoding="gb18030")
    video_node = soup.select_one('#videoShowPage video')

    # video = parse_video_node(video_node=video_node)

    src = video_node.get('data-src')
    base_url = src.split('index.m3u8')[0]
    if not os.path.exists(f'video'):
        os.mkdir(f'video')
    save_m3u8(src, f'video/temp.m3u8')
    append_baseurl_ts(f'video/temp.m3u8', base_url)
    print(f'video/temp.m3u8 done...')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = sys.argv[1]
        start(url)
    else:
        print('Url missed...')
