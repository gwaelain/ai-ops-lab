#!/usr/bin/env bash
# Капельная публикация материалов friendlyai.ru (сайт на GitHub Pages).
#
# Штатно этим занимался бы GitHub Actions, но токен выдан без scope "workflow"
# и GitHub не принимает файл workflow в пуше. Права "repo" хватает, чтобы пушить
# контент, поэтому публикацию раз в сутки делает сервер: пересобирает сайт из
# content/articles/*.md, коммитит, пушит (Pages деплоит сам) и пингует IndexNow.
#
# Ставится в cron на 5.188.27.237:
#   15 7 * * * /opt/drip/ai-ops-lab/tools/drip.sh >> /var/log/friendlyai-drip.log 2>&1
#
# Токен лежит в /root/.git-credentials (chmod 600), в командную строку не попадает.
set -euo pipefail

cd "$(dirname "$0")/.."
echo "=== $(date '+%F %T') drip friendlyai ==="

git config credential.helper store
git pull --quiet --rebase origin main

python3 tools/gen_articles.py

if [ -z "$(git status --porcelain)" ]; then
  echo "изменений нет — публиковать нечего"
  exit 0
fi

git add -A
git -c user.name="gwaelain" -c user.email="mil1000bil@gmail.com" \
    commit -q -m "drip: публикация материалов на $(date +%F)"
git push origin main

python3 tools/indexnow.py
echo "опубликовано и отправлено в IndexNow"
