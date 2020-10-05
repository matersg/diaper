#!/bin/bash
set -e

git -c core.sshCommand="ssh -i ~/.ssh/id_rsa_matersg -F /dev/null" pull
source ../.venv/bin/activate
export PATH=$PATH:`chromedriver-path`
git clean -fx
# scrapy crawl amazon -o amazon.csv
scrapy crawl fairprice -o fairprice.csv
python scrape_redmart.py
python generate_md.py
git add README.md
git commit -m 'auto-update README.md'
git -c core.sshCommand="ssh -i ~/.ssh/id_rsa_matersg -F /dev/null" push
