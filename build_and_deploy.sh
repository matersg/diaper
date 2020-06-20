#!/bin/bash
set -e

git -c core.sshCommand="ssh -i ~/.ssh/id_rsa_matersg -F /dev/null" pull
source ../.venv/bin/activate
rm -v *.csv
scrapy crawl amazon -o amazon.csv
scrapy crawl fairprice -o fairprice.csv
python generate_md.py
git add README.md
git commit -m 'update README.md'
git -c core.sshCommand="ssh -i ~/.ssh/id_rsa_matersg -F /dev/null" push
