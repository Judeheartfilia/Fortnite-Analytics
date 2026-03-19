from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import json
from datetime import datetime
import os
import glob

KNOWN_TAGS = {
    'SIMULATOR', 'TYCOON', 'BATTLE ROYALE', 'DEATHRUN', 'PARKOUR', 'HORROR',
    'ROLEPLAY', 'PVP', 'ZONE WARS', 'BOX FIGHT', 'EDIT COURSE', 'RACING',
    'PARTY', 'SOCIAL', 'SURVIVAL', 'ADVENTURE', 'PUZZLE', 'CREATIVE',
    'MINI GAME', 'SANDBOX', 'SHOOTER', 'RPG', 'STORY', 'ESCAPE',
    'JUST FOR FUN', 'CASUAL', 'COMPETITIVE', 'COOP', 'MULTIPLAYER',
    'SINGLEPLAYER', 'TEAM BATTLE', 'FREE FOR ALL', 'OPEN WORLD',
    'ANIME', 'MOVIE', 'MUSIC', 'SPORT', 'EDUCATIONAL',
}

def extract_all_stats(driver):
    """Extrait toutes les stats visibles depuis le texte de la page"""
    stats = {}

    # Scroll progressif pour déclencher le lazy loading
    for y in [600, 1200, 1800, 2400, 3000]:
        driver.execute_script(f"window.scrollTo(0, {y})")
        time.sleep(1)
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(1)

    page_text = driver.find_element(By.TAG_NAME, 'body').text

    # Description (meta tag)
    html = driver.page_source
    m = re.search(r'<meta[^>]+(?:og:description|name="description")[^>]+content="([^"]+)"', html, re.IGNORECASE)
    if not m:
        m = re.search(r'content="([^"]+)"[^>]+(?:og:description|name="description")', html, re.IGNORECASE)
    if m:
        stats['description'] = m.group(1).strip()

    # Date de publication
    m = re.search(r'RELEASED:\s*([A-Za-z]+ \d+,\s*\d{4})', page_text)
    if m:
        stats['created_date'] = m.group(1).strip()

    # Tags
    found_tags = []
    for line in page_text.split('\n'):
        line = line.strip().upper()
        if line in KNOWN_TAGS:
            found_tags.append(line.title())
    if found_tags:
        stats['tags'] = list(dict.fromkeys(found_tags))

    # Patterns numériques (même logique que scraper_v2.py)
    KMB     = r'(\d+\.?\d*\s*[KMBkmb])'
    NUM_RAW = r'([\d,]+)'
    PCT     = r'(\d+\.?\d*\s*%)'
    MIN_VAL = r'(\d+\.?\d*\s*min)'

    patterns = [
        ('minutes_played',      rf'{KMB}\s*(?:#\d+\s*)?\n\s*Minutes\s+Played'),
        ('favorites_total',     rf'{KMB}\s*(?:#\d+\s*)?\n\s*Favorites'),
        ('peak_ccu_24h',        rf'{NUM_RAW}\s*\n\s*24-HOUR\s+PEAK'),
        ('peak_ccu_alltime',    rf'{NUM_RAW}\s*(?:#\d+\s*)?\n\s*ALL-TIME\s+PEAK'),
        ('players_now',         rf'{NUM_RAW}\s*(?:#\d+\s*)?\n\s*PLAYERS\s+RIGHT\s+NOW'),
        ('unique_players_24h',  rf'Unique\s+Players\s*\n\s*{KMB}'),
        ('recommendations',     rf'Recommendations\s*\n\s*{KMB}'),
        ('avg_playtime',        rf'Average\s+playtime\s*\n\s*{MIN_VAL}'),
        ('avg_session_time',    rf'Average\s+session\s+time\s*\n\s*{MIN_VAL}'),
        ('sessions_24h',        rf'Sessions\s*\n\s*{KMB}'),
        ('retention_d1',        rf'Day\s+1\s+retention\s*\n\s*{PCT}'),
        ('retention_d7',        rf'Day\s+7\s+retention\s*\n\s*{PCT}'),
        ('total_playtime_24h',  rf'Total\s+playtime\s*\n\s*{KMB}'),
        ('favorites',           rf'Favorites\s*\n\s*{KMB}'),
        ('plays_24h',           rf'Plays\s*\n\s*{KMB}'),
        ('players_24h',         rf'Players\s*\n\s*{KMB}'),
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

    # Fallback : peak_ccu_24h → players_24h
    if 'peak_ccu_24h' in stats and 'players_24h' not in stats:
        stats['players_24h'] = stats['peak_ccu_24h']

    return stats


def scrape_island_detailed(driver, code, original_name=''):
    """Scrape tous les détails d'une île"""

    url = f"https://fortnite.gg/island?code={code}"

    try:
        driver.get(url)
        time.sleep(3)

        stats = extract_all_stats(driver)

        # Nom depuis h1
        name = original_name
        try:
            h1 = driver.find_element(By.TAG_NAME, 'h1').text.strip()
            h1 = re.sub(r'\d{4}-\d{4}-\d{4}', '', h1)
            h1 = re.sub(r'\s*-\s*Fortnite.*', '', h1)
            h1 = h1.strip()
            if h1:
                name = h1
        except Exception:
            pass

        island_data = {
            'code': code,
            'name': name or original_name,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            **stats,
        }

        return island_data

    except Exception as e:
        print(f"      ❌ Erreur: {str(e)}")
        return None

def enrich_existing_data():
    """Enrichit les données existantes avec les KPIs détaillés"""
    
    print(f"\n{'='*70}")
    print(f"🔄 ENRICHISSEMENT DES DONNÉES EXISTANTES (VERSION CORRIGÉE)")
    print(f"{'='*70}\n")
    
    # Trouver le fichier pages le plus récent
    files = glob.glob('../data/raw/islands_pages_*.json')
    
    if not files:
        print("❌ Aucun fichier islands_pages_*.json trouvé")
        return None
    
    latest_file = max(files, key=os.path.getctime)
    print(f"📂 Fichier source : {os.path.basename(latest_file)}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        existing_islands = json.load(f)
    
    print(f"✅ {len(existing_islands)} îles à enrichir\n")
    print(f"⏱️  Durée estimée : {len(existing_islands) * 4 / 60:.0f} minutes\n")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Reprise automatique si un fichier checkpoint existe
    existing_checkpoints = glob.glob('../data/raw/islands_enriched_v2_*.json')
    if existing_checkpoints:
        checkpoint_file = max(existing_checkpoints, key=os.path.getctime)
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            enriched_islands = json.load(f)
        already_done = {i['code'] for i in enriched_islands}
        existing_islands = [i for i in existing_islands if i['code'] not in already_done]
        print(f"♻️  Reprise détectée : {len(enriched_islands)} îles déjà scrappées")
        print(f"   Fichier : {os.path.basename(checkpoint_file)}")
        print(f"   Reste : {len(existing_islands)} îles\n")
    else:
        enriched_islands = []
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        checkpoint_file = f'../data/raw/islands_enriched_v2_{timestamp}.json'

    try:
        for i, island in enumerate(existing_islands, 1):
            code = island['code']
            original_name = island.get('name', '')

            print(f"[{i:3d}/{len(existing_islands)}] {code} - {original_name[:30]:30}", end=" ")

            detailed_data = scrape_island_detailed(driver, code, original_name)

            if detailed_data:
                enriched = {**island, **detailed_data}
                enriched_islands.append(enriched)
                print(f"✅")
            else:
                enriched_islands.append(island)
                print(f"⚠️")

            if i % 20 == 0:
                with open(checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(enriched_islands, f, indent=2, ensure_ascii=False)
                print(f"      💾 Sauvegarde : {i} îles → {os.path.basename(checkpoint_file)}")
                print(f"      ⏸️  Pause 5s...")
                time.sleep(5)
            else:
                time.sleep(2)
        
        driver.quit()
        
        # Sauvegarder
        os.makedirs('../data/raw', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'../data/raw/islands_enriched_v2_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(enriched_islands, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ ENRICHISSEMENT TERMINÉ")
        print(f"💾 Fichier : {filename}")
        print(f"📊 {len(enriched_islands)} îles")
        print(f"{'='*70}\n")
        
        # Stats
        stats = {
            'players_24h': len([i for i in enriched_islands if i.get('players_24h', 'N/A') != 'N/A']),
            'retention_d1': len([i for i in enriched_islands if i.get('retention_d1', 'N/A') != 'N/A']),
        }
        
        print("📈 NOUVEAUX KPIs :")
        for metric, count in stats.items():
            pct = (count / len(enriched_islands) * 100) if enriched_islands else 0
            print(f"   {metric}: {count}/{len(enriched_islands)} ({pct:.0f}%)")
        
        print(f"\n{'='*70}")
        print("📂 Prochaines étapes :")
        print("   1. py -3.9 clean_data_enriched.py")
        print("   2. py -3.9 categorize_islands.py")
        print("   3. cd ../dashboard && py -3.9 update_dashboard.py")
        print(f"{'='*70}\n")
        
        return enriched_islands
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            driver.quit()
        except:
            pass
        return None

if __name__ == "__main__":
    islands = enrich_existing_data()