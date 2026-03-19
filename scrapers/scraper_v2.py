"""
Scraper V2 - Extraction complète de tous les KPIs par île
Charge les 260 codes existants et enrichit avec les champs manquants :
  - peak_ccu, avg_ccu, plays_24h
  - avg_playtime, avg_session_time
  - created_date (date de sortie)
  - description, tags (pour améliorer la catégorisation)

Reprend automatiquement là où il s'est arrêté si un fichier partiel existe.
"""

import json
import os
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW    = os.path.join(SCRIPTS_DIR, '..', 'data', 'raw')
DATA_PROC   = os.path.join(SCRIPTS_DIR, '..', 'data', 'processed')


def extract_all_stats(driver):
    """Extrait toutes les stats et métadonnées visibles de la page."""
    stats = {}

    # Scroll progressif pour charger tout le contenu lazy (section 24H OVERVIEW)
    for y in [600, 1200, 1800, 2400, 3000]:
        driver.execute_script(f"window.scrollTo(0, {y})")
        time.sleep(1.5)
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    page_text = driver.find_element(By.TAG_NAME, 'body').text

    # ── Description (meta og:description) ─────────────────────────────────
    for selector in [{'property': 'og:description'}, {'name': 'description'}]:
        tag = soup.find('meta', selector)
        if tag and tag.get('content', '').strip():
            stats['description'] = tag['content'].strip()
            break

    # ── Date de publication ────────────────────────────────────────────────
    # Format page: "RELEASED: Jul 5, 2025"
    m = re.search(r'RELEASED:\s*([A-Za-z]+ \d+,\s*\d{4})', page_text)
    if m:
        stats['created_date'] = m.group(1).strip()

    m = re.search(r'UPDATED:\s*([A-Za-z]+ \d+,\s*\d{4})', page_text)
    if m:
        stats['updated_date'] = m.group(1).strip()

    # ── Tags fortnite.gg ───────────────────────────────────────────────────
    # Ils apparaissent entre "FORTNITE.COM" et la description (ex: SIMULATOR, TYCOON...)
    # Liste des catégories connues de fortnite.gg
    KNOWN_TAGS = {
        'SIMULATOR', 'TYCOON', 'BATTLE ROYALE', 'DEATHRUN', 'PARKOUR', 'HORROR',
        'ROLEPLAY', 'PVP', 'ZONE WARS', 'BOX FIGHT', 'EDIT COURSE', 'RACING',
        'PARTY', 'SOCIAL', 'SURVIVAL', 'ADVENTURE', 'PUZZLE', 'CREATIVE',
        'MINI GAME', 'SANDBOX', 'SHOOTER', 'RPG', 'STORY', 'ESCAPE',
        'JUST FOR FUN', 'CASUAL', 'COMPETITIVE', 'COOP', 'MULTIPLAYER',
        'SINGLEPLAYER', 'TEAM BATTLE', 'FREE FOR ALL', 'OPEN WORLD',
        'ANIME', 'MOVIE', 'MUSIC', 'SPORT', 'EDUCATIONAL',
    }
    found_tags = []
    for line in page_text.split('\n'):
        line = line.strip().upper()
        if line in KNOWN_TAGS:
            found_tags.append(line.title())
    if found_tags:
        stats['tags'] = list(dict.fromkeys(found_tags))

    # ── Stats numériques ───────────────────────────────────────────────────
    # La page fortnite.gg a deux zones :
    # 1. En-tête  : VALUE [#RANK] \n LABEL  (ex: "22.4B #10\nMinutes Played")
    # 2. 24H OVERVIEW : LABEL \n VALUE [#RANK]  (ex: "Unique Players\n2.2M #3")
    #
    # Les nombres en-tête utilisent K/M/B ou des entiers avec virgules (958,485)
    # Les nombres 24H OVERVIEW utilisent K/M/B ou "XX.XX min"

    KMB     = r'(\d+\.?\d*\s*[KMBkmb])'          # ex: 2.4M, 285K, 22.4B
    NUM_RAW = r'([\d,]+)'                          # ex: 958,485
    PCT     = r'(\d+\.?\d*\s*%)'                  # ex: 66%
    MIN_VAL = r'(\d+\.?\d*\s*min)'                # ex: 75.08 min

    patterns = [
        # ── EN-TÊTE (value → label) ──────────────────────────────────────
        ('minutes_played',    rf'{KMB}\s*(?:#\d+\s*)?\n\s*Minutes\s+Played'),
        ('favorites_total',   rf'{KMB}\s*(?:#\d+\s*)?\n\s*Favorites'),
        ('peak_ccu_24h',      rf'{NUM_RAW}\s*\n\s*24-HOUR\s+PEAK'),
        ('peak_ccu_alltime',  rf'{NUM_RAW}\s*(?:#\d+\s*)?\n\s*ALL-TIME\s+PEAK'),
        ('players_now',       rf'{NUM_RAW}\s*(?:#\d+\s*)?\n\s*PLAYERS\s+RIGHT\s+NOW'),
        # ── 24H OVERVIEW (label → value) ─────────────────────────────────
        ('unique_players_24h',  rf'Unique\s+Players\s*\n\s*{KMB}'),
        ('favorites_24h',       rf'(?<=24H OVERVIEW\n)(?:.*?\n)*?Favorites\s*\n\s*{KMB}'),
        ('recommendations',     rf'Recommendations\s*\n\s*{KMB}'),
        ('avg_playtime',        rf'Average\s+playtime\s*\n\s*{MIN_VAL}'),
        ('avg_session_time',    rf'Average\s+session\s+time\s*\n\s*{MIN_VAL}'),
        ('sessions_24h',        rf'Sessions\s*\n\s*{KMB}'),
        ('retention_d1',        rf'Day\s+1\s+retention\s*\n\s*{PCT}'),
        ('retention_d7',        rf'Day\s+7\s+retention\s*\n\s*{PCT}'),
        ('total_playtime_24h',  rf'Total\s+playtime\s*\n\s*{KMB}'),
    ]

    for field, pattern in patterns:
        try:
            m = re.search(pattern, page_text, re.IGNORECASE | re.MULTILINE)
            if m:
                val = m.group(1).strip().replace(',', '')
                if val and val not in ('0', '0%'):
                    stats[field] = val
        except Exception:
            pass

    # Alias : players_24h = peak_ccu_24h (meilleure approximation disponible)
    if 'peak_ccu_24h' in stats and 'players_24h' not in stats:
        stats['players_24h'] = stats['peak_ccu_24h']

    return stats


def scrape_island(driver, code, original_name=''):
    """Scrape complet d'une île : nom + toutes les stats."""
    url = f"https://fortnite.gg/island?code={code}"

    try:
        driver.get(url)
        time.sleep(7)

        # Nom
        name = original_name or 'Unknown'
        try:
            h1 = driver.find_element(By.TAG_NAME, 'h1')
            raw = h1.text.strip()
            raw = re.sub(r'\d{4}-\d{4}-\d{4}', '', raw).strip()
            raw = re.sub(r'\s*-?\s*Fortnite.*', '', raw, flags=re.IGNORECASE).strip()
            raw = re.sub(r'\s*by\s+\S+.*', '', raw, flags=re.IGNORECASE).strip()
            if raw:
                name = raw
        except Exception:
            pass

        stats = extract_all_stats(driver)

        return {
            'code': code,
            'name': name,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            **stats,
        }

    except Exception as e:
        print(f"  ERREUR: {e}")
        return None


def scrape_v2(headless=False):
    # ── Charger les codes depuis les données catégorisées ─────────────────
    cat_file = os.path.join(DATA_PROC, 'islands_categorized.json')
    with open(cat_file, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    codes = [(i['code'], i.get('name', '')) for i in existing]
    total = len(codes)

    print(f"\n{'='*60}")
    print(f"SCRAPER V2 - {total} iles")
    print(f"Duree estimee: ~{total * 9 / 60:.0f} minutes")
    print(f"{'='*60}\n")

    # ── Reprise : chercher un fichier partiel ─────────────────────────────
    partial_files = sorted(
        [f for f in os.listdir(DATA_RAW) if f.startswith('islands_v2_')],
        reverse=True
    )

    already_scraped = {}
    output_file = os.path.join(DATA_RAW, f"islands_v2_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json")

    if partial_files:
        latest = os.path.join(DATA_RAW, partial_files[0])
        print(f"Reprise depuis: {partial_files[0]}")
        with open(latest, 'r', encoding='utf-8') as f:
            partial = json.load(f)
        already_scraped = {i['code']: i for i in partial}
        output_file = latest  # On écrase le partiel pour ne pas multiplier les fichiers
        print(f"{len(already_scraped)} iles deja scraped - on continue\n")

    # ── Initialiser Chrome (undetected pour bypass Cloudflare) ───────────
    opts = uc.ChromeOptions()
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--window-size=1920,1080')

    driver = uc.Chrome(options=opts, headless=headless, use_subprocess=True, version_main=145)

    results = dict(already_scraped)

    try:
        for i, (code, name) in enumerate(codes, 1):
            if code in already_scraped:
                print(f"[{i:3d}/{total}] SKIP  {code}")
                continue

            print(f"[{i:3d}/{total}] {code}  {name[:30]:30}", end="  ")

            data = scrape_island(driver, code, name)

            if data:
                results[code] = data
                got = [
                    k for k in [
                        'players_24h', 'peak_ccu_24h', 'plays_24h',
                        'avg_playtime', 'created_date', 'description', 'tags'
                    ]
                    if data.get(k) not in (None, '', 'N/A', [])
                ]
                print(f"OK  [{', '.join(got)}]")
            else:
                results[code] = {
                    'code': code,
                    'name': name,
                    'url': f'https://fortnite.gg/island?code={code}',
                    'scraped_at': datetime.now().isoformat(),
                }
                print("FAIL")

            # Sauvegarde incrémentale toutes les 20 îles
            if i % 20 == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(list(results.values()), f, indent=2, ensure_ascii=False)
                print(f"  >> Sauvegarde intermediaire: {len(results)}/{total} iles")

            time.sleep(8 if i % 10 == 0 else 4)

        driver.quit()

    except Exception as e:
        print(f"\nERREUR: {e}")
        try:
            driver.quit()
        except Exception:
            pass

    # Sauvegarde finale
    final = list(results.values())
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"TERMINE: {len(final)} iles")
    print(f"Fichier: {os.path.basename(output_file)}")

    fields = [
        'players_24h', 'peak_ccu_24h', 'plays_24h',
        'avg_playtime', 'avg_session_time', 'created_date',
        'description', 'tags',
    ]
    print("\nTaux de collecte:")
    for field in fields:
        count = sum(
            1 for r in final
            if r.get(field) not in (None, '', 'N/A', [], 0)
        )
        pct = count / len(final) * 100 if final else 0
        icon = "OK" if pct > 70 else ("~" if pct > 30 else "X")
        print(f"  [{icon}] {field:25} {count:3}/{len(final)}  ({pct:.0f}%)")

    print(f"\nProchaine etape:")
    print(f"  python clean_data_enriched.py")
    print(f"{'='*60}\n")

    return final


if __name__ == "__main__":
    scrape_v2(headless=False)
