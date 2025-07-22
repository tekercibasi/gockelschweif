# gockelschweif

This repository contains a simple crawler script for exporting the contents of a website to Markdown files. The script was written to help migrate the contents of **allmendina.de** into a wiki-style system.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the crawler:
   ```bash
   python crawler.py https://allmendina.de --outdir output
   ```
   The resulting Markdown files will be written to the specified directory.

Note: actual crawling might fail in restricted environments. The script expects internet access.
