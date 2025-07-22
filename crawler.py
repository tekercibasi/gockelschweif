import argparse
import os
import re
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


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
    md = []
    for elem in soup.body.recursiveChildGenerator():
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
        soup = BeautifulSoup(r.text, 'html.parser')
        slug = slugify(urlparse(url).path or 'index')
        md = html_to_markdown(soup)
        with open(os.path.join(outdir, slug + '.md'), 'w', encoding='utf-8') as f:
            f.write(md)
        for link in extract_links(soup, url, visited):
            queue.append(link)


def main():
    parser = argparse.ArgumentParser(description='Crawl a site and output Markdown files.')
    parser.add_argument('url', help='Base URL to crawl')
    parser.add_argument('--outdir', default='output', help='Directory for Markdown output')
    args = parser.parse_args()
    crawl(args.url, args.outdir)


if __name__ == '__main__':
    main()
