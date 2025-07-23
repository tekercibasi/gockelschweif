import argparse
import os
import re
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    print("Error: missing dependency 'beautifulsoup4'.")
    print("Install it with `pip install -r requirements.txt` and re-run the script.")
    raise


def slugify(text: str) -> str:
    text = re.sub(r'\W+', '-', text.lower())
    return text.strip('-') or 'index'


def extract_links(soup, base_url, visited):
    for a in soup.find_all('a', href=True):
        href = urljoin(base_url, a['href'])
        parsed = urlparse(href)
        if parsed.netloc == urlparse(base_url).netloc:
            if href not in visited:
                yield href


def html_to_markdown(soup):
    if soup.body is None:
        return ''
    md = []
    # BeautifulSoup's recursiveChildGenerator was deprecated in 4.0.0; use
    # the descendants generator instead.
    for elem in soup.body.descendants:

        if getattr(elem, 'name', None):
            if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(elem.name[1])
                text = elem.get_text(strip=True)
                md.append('#' * level + ' ' + text)
            elif elem.name == 'p':
                text = elem.get_text(strip=True)
                if text:
                    md.append(text)
            elif elem.name == 'ul':
                for li in elem.find_all('li', recursive=False):
                    md.append('- ' + li.get_text(strip=True))
            elif elem.name == 'img':
                alt = elem.get('alt', '').strip() or 'TODO: add alt text'
                src = elem.get('src')
                if src:
                    md.append(f'![{alt}]({src})')
            elif elem.name == 'a' and elem.get('href'):
                text = elem.get_text(strip=True) or elem['href']
                href = elem['href']
                md.append(f'[{text}]({href})')
    return '\n\n'.join(md)


def crawl(base_url, outdir='output'):
    os.makedirs(outdir, exist_ok=True)
    visited = set()
    queue = deque([base_url])
    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        try:
            r = requests.get(url)
        except requests.RequestException as e:
            print(f'Failed to fetch {url}: {e}')
            continue
        content_type = r.headers.get('content-type', '')
        if 'xml' in content_type or url.lower().endswith('.xml'):
            parser = 'xml'
        else:
            parser = 'html.parser'
        soup = BeautifulSoup(r.text, parser)
        slug = slugify(urlparse(url).path or 'index')
        md = html_to_markdown(soup)
        with open(os.path.join(outdir, slug + '.md'), 'w', encoding='utf-8') as f:
            f.write(md)
        for link in extract_links(soup, url, visited):
            queue.append(link)


DEFAULT_URL = "https://allmendina.de"



def main():
    parser = argparse.ArgumentParser(
        description='Crawl a website and output Markdown files.'
    )
    parser.add_argument(
        'url', nargs='?', default=DEFAULT_URL,
        help='Base URL to crawl (default: %(default)s)'
    )
    parser.add_argument(
        '--outdir', default='output', help='Directory for Markdown output'
    )
    args = parser.parse_args()
    crawl(args.url, args.outdir)


if __name__ == '__main__':
    main()
