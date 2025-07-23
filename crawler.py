import argparse
import os
import re
import time
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


def generate_outdir(base_url: str) -> str:
    """Create a default output directory name from the domain and current time."""
    parsed = urlparse(base_url if '://' in base_url else f'https://{base_url}')
    domain = (parsed.netloc or parsed.path).split('/')[0]
    timestamp = time.strftime('%Y_%m_%d_%H.%M.%S')
    return f'output_{domain}_{timestamp}'


def extract_links(soup, base_url, visited):
    for a in soup.find_all('a', href=True):
        href = urljoin(base_url, a['href'])
        parsed = urlparse(href)
        if parsed.netloc == urlparse(base_url).netloc:
            if href not in visited:
                yield href


def process_images(soup, base_url, images_dir, counter):
    os.makedirs(images_dir, exist_ok=True)
    log_path = os.path.join(images_dir, "image_sources.txt")
    log_lines = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        img_url = urljoin(base_url, src)
        try:
            resp = requests.get(img_url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            continue
        ext = os.path.splitext(urlparse(img_url).path)[1] or ".img"
        local_name = f"img{counter[0]}{ext}"
        counter[0] += 1
        with open(os.path.join(images_dir, local_name), "wb") as fh:
            fh.write(resp.content)
        log_lines.append(f"{local_name} {img_url}\n")
        img["src"] = f"images/{local_name}"
    if log_lines:
        with open(log_path, "a", encoding="utf-8") as log_file:
            for line in log_lines:
                log_file.write(line)


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
    images_dir = os.path.join(outdir, 'images')
    visited = set()
    queue = deque([base_url])
    img_counter = [1]
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
        process_images(soup, url, images_dir, img_counter)
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
        '--outdir', help='Directory for Markdown output'
    )
    args = parser.parse_args()
    outdir = args.outdir or generate_outdir(args.url)
    crawl(args.url, outdir)


if __name__ == '__main__':
    main()

