"""
Scraper Fortnite Creative via API officielle Epic Games
https://api.fortnite.com/ecosystem/v1

- Pas de navigateur, pas de Cloudflare
- Fonctionne depuis GitHub Actions
- ~5-10 minutes pour toutes les iles
"""

import urllib.request
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://api.fortnite.com/ecosystem/v1"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}
MAX_WORKERS = 10   # requetes paralleles
TIMEOUT     = 15   # secondes


def api_get(path):
    url = BASE_URL + path
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        r = urllib.request.urlopen(req, timeout=TIMEOUT)
        return json.loads(r.read())
    except Exception as e:
        return None


def fetch_all_islands(max_islands=2000):
    """Recupere les codes d'iles depuis le fichier local (iles populaires)
    ou via l'API si pas de fichier local."""
    import glob

    # Chercher un fichier de codes iles populaires (scrape fortnite.gg)
    files = glob.glob('../data/raw/islands_pages_*.json')
    if files:
        latest = max(files, key=os.path.getctime)
        print(f"Utilisation du fichier local : {os.path.basename(latest)}")
        with open(latest, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        islands = [{'code': i['code'], 'title': i.get('name',''), 'tags': [], 'creatorCode': ''} for i in raw]
        print(f"Total : {len(islands)} iles")
        return islands

    # Sinon, fallback sur l'API
    islands = []
    cursor  = None
    page    = 0
    print(f"Recuperation de la liste des iles via API (max {max_islands})...")
    while len(islands) < max_islands:
        path = "/islands?limit=100"
        if cursor:
            path += f"&after={cursor}"
        data = api_get(path)
        if not data:
            break
        batch = data.get("data", [])
        islands.extend(batch)
        page += 1

        next_link = data.get("links", {}).get("next")
        if not next_link:
            break

        cursor = data["meta"]["page"]["nextCursor"]

        if page % 10 == 0:
            print(f"  {len(islands)} iles recuperees...")

    print(f"Total : {len(islands)} iles")
    return islands


def fetch_island_metrics(code, start_date, end_date):
    """Recupere les metriques d'une ile pour une periode donnee"""
    path = f"/islands/{code}/metrics?start_date={start_date}&end_date={end_date}&interval=day"
    return api_get(path)


def get_last_value(series):
    """Retourne la derniere valeur d'une serie temporelle"""
    if not series:
        return None
    return series[-1].get("value")


def format_number(n):
    """Formate un nombre en K/M"""
    if n is None:
        return "N/A"
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def scrape_all():
    today     = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"\n{'='*70}")
    print(f"SCRAPING VIA API OFFICIELLE EPIC GAMES")
    print(f"Periode : {yesterday} -> {today}")
    print(f"Demarre a {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    # 1. Recuperer toutes les iles
    island_list = fetch_all_islands(max_islands=2000)
    if not island_list:
        print("Aucune ile recuperee !")
        return None

    # 2. Recuperer les metriques en parallele
    print(f"\nRecuperation des metriques ({MAX_WORKERS} requetes paralleles)...")
    results     = []
    errors      = 0
    done        = 0

    def process_island(island_meta):
        code    = island_meta["code"]
        metrics = fetch_island_metrics(code, yesterday, today)
        return island_meta, metrics

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_island, i): i for i in island_list}

        for future in as_completed(futures):
            done += 1
            island_meta, metrics = future.result()
            code  = island_meta["code"]
            title = island_meta.get("title", "Unknown")

            if metrics:
                # Prendre les valeurs du dernier jour disponible
                unique_players = get_last_value(metrics.get("uniquePlayers"))
                plays          = get_last_value(metrics.get("plays"))
                peak_ccu       = get_last_value(metrics.get("peakCCU"))
                favorites      = get_last_value(metrics.get("favorites"))
                recommends     = get_last_value(metrics.get("recommendations"))
                avg_playtime   = get_last_value(metrics.get("averageMinutesPerPlayer"))
                minutes_played = get_last_value(metrics.get("minutesPlayed"))

                # Retention : derniere entree
                retention_list = metrics.get("retention", [])
                d1_raw = retention_list[-1].get("d1") if retention_list else None
                d7_raw = retention_list[-1].get("d7") if retention_list else None
                d1 = d1_raw * 100 if d1_raw is not None else None
                d7 = d7_raw * 100 if d7_raw is not None else None

                island = {
                    "code":                  code,
                    "name":                  title,
                    "url":                   f"https://fortnite.gg/island?code={code}",
                    "creator":               island_meta.get("creatorCode", ""),
                    "tags":                  island_meta.get("tags", []),
                    "created_in":            island_meta.get("createdIn", ""),

                    "players_24h":           int(unique_players) if unique_players else 0,
                    "players_display":       format_number(unique_players),

                    "plays_24h":             int(plays) if plays else 0,
                    "plays_display":         format_number(plays),

                    "peak_ccu_24h":          int(peak_ccu) if peak_ccu else 0,
                    "peak_ccu_24h_display":  format_number(peak_ccu),

                    "favorites":             int(favorites) if favorites else 0,
                    "favorites_display":     format_number(favorites),

                    "recommendations":       int(recommends) if recommends else 0,
                    "recommendations_display": format_number(recommends),

                    "avg_playtime":          round(avg_playtime, 1) if avg_playtime else None,
                    "avg_playtime_display":  f"{round(avg_playtime, 1)} min" if avg_playtime else "N/A",

                    "minutes_played":        int(minutes_played) if minutes_played else 0,

                    "retention_d1":          round(d1, 1) if d1 is not None else 0,
                    "retention_d1_display":  f"{round(d1, 1)}%" if d1 is not None else "N/A",

                    "retention_d7":          round(d7, 1) if d7 is not None else 0,
                    "retention_d7_display":  f"{round(d7, 1)}%" if d7 is not None else "N/A",

                    "scraped_at":            datetime.now().isoformat(),
                }
                results.append(island)
            else:
                errors += 1

            if done % 100 == 0:
                print(f"  [{done}/{len(island_list)}] {len(results)} OK, {errors} erreurs")

    # 3. Trier par joueurs
    results.sort(key=lambda x: x["players_24h"], reverse=True)

    # 4. Sauvegarder
    os.makedirs("../data/processed", exist_ok=True)
    output = "../data/processed/islands_clean.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"TERMINE !")
    print(f"Iles avec donnees : {len(results)}")
    print(f"Erreurs           : {errors}")
    print(f"Fichier           : {output}")
    print(f"\nTop 3 :")
    for i, isle in enumerate(results[:3], 1):
        print(f"  {i}. {isle['name'][:40]} - {isle['players_display']} joueurs")
    print(f"{'='*70}\n")

    return results


if __name__ == "__main__":
    scrape_all()
