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

def scrape_island_precise(driver, code):
    """Scrape PRÉCIS d'une île avec extraction visuelle"""
    
    url = f"https://fortnite.gg/island?code={code}"
    
    try:
        driver.get(url)
        time.sleep(6)  # Plus de temps pour chargement complet
        
        # Nom depuis h1
        try:
            h1 = driver.find_element(By.TAG_NAME, 'h1')
            name = h1.text.strip()
            name = re.sub(r'\d{4}-\d{4}-\d{4}', '', name).strip()
            name = re.sub(r'\s*by\s+.*', '', name).strip()
        except:
            name = 'Unknown'
        
        # Méthode VISUELLE : Chercher les éléments contenant les stats
        stats_data = {}
        
        # Chercher tous les divs/spans avec des nombres
        try:
            # Players 24h - chercher le texte "Players" puis le nombre à côté
            players_elem = driver.find_elements(By.XPATH, "//*[contains(text(), 'Players') or contains(text(), 'PLAYERS')]")
            for elem in players_elem:
                parent = elem.find_element(By.XPATH, '..')
                text = parent.text
                # Chercher un nombre avec K/M dans le même bloc
                match = re.search(r'(\d+\.?\d*[KM])\s*(?:Players|PLAYERS)', text, re.IGNORECASE)
                if not match:
                    match = re.search(r'(?:Players|PLAYERS)\s*(\d+\.?\d*[KM])', text, re.IGNORECASE)
                if match:
                    stats_data['players_24h'] = match.group(1)
                    break
        except:
            pass
        
        # Plays 24h
        try:
            plays_elem = driver.find_elements(By.XPATH, "//*[contains(text(), 'Plays')]")
            for elem in plays_elem:
                parent = elem.find_element(By.XPATH, '..')
                text = parent.text
                match = re.search(r'(\d+\.?\d*[KM])\s*Plays', text, re.IGNORECASE)
                if not match:
                    match = re.search(r'Plays\s*(\d+\.?\d*[KM])', text, re.IGNORECASE)
                if match:
                    stats_data['plays_24h'] = match.group(1)
                    break
        except:
            pass
        
        # Favorites
        try:
            fav_elem = driver.find_elements(By.XPATH, "//*[contains(text(), 'Favorites')]")
            for elem in fav_elem:
                parent = elem.find_element(By.XPATH, '..')
                text = parent.text
                match = re.search(r'(\d+\.?\d*[KM])\s*Favorites', text, re.IGNORECASE)
                if not match:
                    match = re.search(r'Favorites\s*(\d+\.?\d*[KM])', text, re.IGNORECASE)
                if match:
                    stats_data['favorites'] = match.group(1)
                    break
        except:
            pass
        
        # Recommendations
        try:
            rec_elem = driver.find_elements(By.XPATH, "//*[contains(text(), 'Recommendations')]")
            for elem in rec_elem:
                parent = elem.find_element(By.XPATH, '..')
                text = parent.text
                match = re.search(r'(\d+\.?\d*[KM])\s*Recommendations', text, re.IGNORECASE)
                if not match:
                    match = re.search(r'Recommendations\s*(\d+\.?\d*[KM])', text, re.IGNORECASE)
                if match:
                    stats_data['recommendations'] = match.group(1)
                    break
        except:
            pass
        
        # Unique Players
        try:
            unique_elem = driver.find_elements(By.XPATH, "//*[contains(text(), 'Unique Players')]")
            for elem in unique_elem:
                parent = elem.find_element(By.XPATH, '..')
                text = parent.text
                match = re.search(r'(\d+\.?\d*[KM])\s*Unique', text, re.IGNORECASE)
                if not match:
                    match = re.search(r'Unique\s+Players\s*(\d+\.?\d*[KM])', text, re.IGNORECASE)
                if match:
                    stats_data['unique_players_24h'] = match.group(1)
                    break
        except:
            pass
        
        # Day 1 Retention
        try:
            ret_elem = driver.find_elements(By.XPATH, "//*[contains(text(), 'Day 1 Retention')]")
            for elem in ret_elem:
                parent = elem.find_element(By.XPATH, '..')
                text = parent.text
                match = re.search(r'(\d+\.?\d*%)', text)
                if match:
                    stats_data['retention_d1'] = match.group(1)
                    break
        except:
            pass
        
        # Day 7 Retention
        try:
            ret_elem = driver.find_elements(By.XPATH, "//*[contains(text(), 'Day 7 Retention')]")
            for elem in ret_elem:
                parent = elem.find_element(By.XPATH, '..')
                text = parent.text
                match = re.search(r'(\d+\.?\d*%)', text)
                if match:
                    stats_data['retention_d7'] = match.group(1)
                    break
        except:
            pass
        
        island_data = {
            'code': code,
            'name': name,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'players_24h': stats_data.get('players_24h', 'N/A'),
            'plays_24h': stats_data.get('plays_24h', 'N/A'),
            'unique_players_24h': stats_data.get('unique_players_24h', 'N/A'),
            'favorites': stats_data.get('favorites', 'N/A'),
            'recommendations': stats_data.get('recommendations', 'N/A'),
            'retention_d1': stats_data.get('retention_d1', 'N/A'),
            'retention_d7': stats_data.get('retention_d7', 'N/A'),
        }
        
        return island_data
        
    except Exception as e:
        print(f"      ❌ Erreur: {str(e)}")
        return None

def enrich_precise():
    """Enrichissement PRÉCIS"""
    
    print(f"\n{'='*70}")
    print(f"🎯 ENRICHISSEMENT ULTRA-PRÉCIS")
    print(f"{'='*70}\n")
    
    files = glob.glob('../data/raw/islands_pages_*.json')
    
    if not files:
        print("❌ Aucun fichier trouvé")
        return None
    
    latest_file = max(files, key=os.path.getctime)
    print(f"📂 Source : {os.path.basename(latest_file)}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        islands = json.load(f)
    
    # TEST avec les 10 premières seulement
    islands_test = islands[:10]
    
    print(f"✅ Test avec {len(islands_test)} îles\n")
    
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    enriched = []
    
    try:
        for i, island in enumerate(islands_test, 1):
            code = island['code']
            print(f"[{i:2d}/{len(islands_test)}] {code}", end=" → ")
            
            data = scrape_island_precise(driver, code)
            
            if data:
                enriched.append({**island, **data})
                print(f"✅ {data['name'][:30]} | Players: {data['players_24h']} | Fav: {data['favorites']}")
            else:
                enriched.append(island)
                print(f"❌")
            
            time.sleep(3)
        
        driver.quit()
        
        # Sauvegarder
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'../data/raw/islands_precise_test_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(enriched, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ TEST TERMINÉ")
        print(f"💾 {filename}")
        print(f"{'='*70}\n")
        
        print("📊 VÉRIFICATION :\n")
        for island in enriched[:5]:
            print(f"   {island.get('name', 'Unknown')[:40]:40} | {island.get('players_24h', 'N/A')}")
        
        return enriched
        
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
    islands = enrich_precise()