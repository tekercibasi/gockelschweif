# gockelschweif

This repository contains a simple crawler script for exporting the contents of a website to Markdown files. The script was written to help migrate the contents of **allmendina.de** into a wiki-style system.

## Usage

1. Install dependencies (requires `lxml` for XML parsing):
   ```bash
   pip install -r requirements.txt
   ```
   If you see `ModuleNotFoundError: No module named 'bs4'`, install the dependencies first.

2. Run the crawler. Provide the URL you want to crawl (defaults to
   `https://allmendina.de`):
   ```bash
   python crawler.py https://allmendina.de --outdir output

   ```
   The resulting Markdown files will be written to the specified directory.

The crawler inspects response headers to detect XML pages. If an XML
document is requested (for example RSS feeds), it parses the response
with BeautifulSoup's `xml` parser, otherwise it falls back to the HTML
parser.

Note: actual crawling might fail in restricted environments. The script expects internet access.
