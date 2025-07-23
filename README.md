# gockelschweif

This repository contains a simple crawler script for exporting the contents of a website to Markdown files. The script was written to help migrate the contents of **allmendina.de** into a wiki-style system.

## Usage

1. Install dependencies:
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
   Any images referenced on the pages are downloaded to `output/images`
   with simplified names (e.g. `img1.jpg`). A mapping of original URLs
   is stored in `image_sources.txt` within that folder.

Note: actual crawling might fail in restricted environments. The script expects internet access.
