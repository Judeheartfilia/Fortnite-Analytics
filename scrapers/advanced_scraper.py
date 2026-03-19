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

def scrape_island_details(driver, code):
    """Scrape les détails complets d'une île spécifique"""
    
    url = f"https://fortnite.gg/creative?code={code}"
    
    try:
        driver.get(url)
        time.sleep(3)
        
        html = driver.page_source
        
        island_data = {
            'code': code,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Patterns de recherche pour chaque métrique
        metrics_patterns = {
            'minutes_played': r'Minutes Played[^\d]*([\d,\.]+[KMB]?)',
            'plays': r'(?:Plays|24h Plays)[^\d]*([\d,\.]+[KMB]?)',
            'peak_ccu': r'(?:Peak|All-Time Peak)[^\d]*([\d,\.]+[KMB]?)',
            'unique_players': r'(?:Players|Unique Players|24h Players)[^\d]*([\d,\.]+[KMB]?)',
            'favorites': r'(?:Favorites|24h Favorites)[^\d]*([\d,\.]+[KMB]?)',
            'recommends': r'(?:Recommends|24h Recs)[^\d]*([\d,\.]+[KMB]?)',
            'avg_playtime': r'(?:Avg Playtime|24h Avg Playtime)[^\d]*([\d,\.]+)',
            'retention': r'(?:Retention|24h Retention)[^\d]*([\d,\.]+%)',
        }
        
        print(f"\n🔍 Scraping {code}...")
        
        # Extraire chaque métrique
        for metric_name, pattern in metrics_patterns.items():
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                island_data[metric_name] = matches[0]
                print(f"   ✅ {metric_name}: {matches[0]}")
            else:
                island_data[metric_name] = 'N/A'
        
        # Nom
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if title_match:
            island_data['name'] = title_match.group(1).replace(' - Fortnite.GG', '').strip()
            print(f"   ✅ name: {island_data['name']}")
        
        # Date de sortie
        date_patterns = [
            r'(?:Created|Released|Added)[^\d]*([\d]{1,2}[/-][\d]{1,2}[/-][\d]{2,4})',
            r'(?:Date)[^\d]*([\d]{4}-[\d]{2}-[\d]{2})'
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, html, re.IGNORECASE)
            if date_match:
                island_data['release_date'] = date_match.group(1)
                print(f"   ✅ release_date: {date_match.group(1)}")
                break
        
        # Tags/genres
        tags = re.findall(r'<span[^>]*class="[^"]*tag[^"]*"[^>]*>(.*?)</span>', html, re.IGNORECASE)
        if tags:
            island_data['tags'] = [tag.strip() for tag in tags if len(tag.strip()) > 2]
            if island_data['tags']:
                print(f"   ✅ tags: {', '.join(island_data['tags'][:3])}")
        
        return island_data
        
    except Exception as e:
        print(f"   ❌ Erreur sur {code}: {str(e)}")
        return None

def scrape_all_islands_detailed(limit=None):
    """Scrape la liste des îles + détails complets de chacune"""
    
    print(f"\n{'='*70}")
    print(f"🚀 FORTNITE CREATIVE ANALYTICS - SCRAPING AVANCÉ")
    print(f"🕐 Démarré à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    all_islands_data = []
    
    try:
        # ÉTAPE 1 : Liste des îles
        print("📋 ÉTAPE 1 : Récupération de la liste des îles\n")
        
        driver.get("https://fortnite.gg/creative")
        time.sleep(5)
        
        # Cookies
        try:
            driver.find_element(By.XPATH, "//button[contains(text(), 'Consent')]").click()
            time.sleep(2)
        except:
            pass
        
        # Scroll
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Extraire codes
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        codes = []
        
        for link in all_links:
            try:
                href = link.get_attribute('href')
                if href and 'code=' in href:
                    code_match = re.search(r'code=(\d{4}-\d{4}-\d{4})', href)
                    if code_match:
                        codes.append(code_match.group(1))
            except:
                continue
        
        codes = list(set(codes))
        
        if limit:
            codes = codes[:limit]
        
        print(f"✅ {len(codes)} îles trouvées")
        print(f"📊 Scraping détaillé de {len(codes)} îles...\n")
        
        # ÉTAPE 2 : Détails de chaque île
        print(f"{'='*70}")
        print(f"📊 ÉTAPE 2 : Scraping détaillé")
        print(f"⏱️  Durée estimée : {len(codes) * 3 / 60:.1f} minutes")
        print(f"{'='*70}")
        
        for i, code in enumerate(codes, 1):
            print(f"\n[{i}/{len(codes)}] ", end="")
            
            island_data = scrape_island_details(driver, code)
            
            if island_data:
                all_islands_data.append(island_data)
            
            time.sleep(2)
        
        # Sauvegarder
        os.makedirs('../data/raw', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'../data/raw/islands_detailed_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_islands_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ SCRAPING TERMINÉ")
        print(f"💾 Fichier: {filename}")
        print(f"📊 {len(all_islands_data)} îles avec métriques complètes")
        print(f"{'='*70}\n")
        
        # Résumé
        print("📈 RÉSUMÉ DES MÉTRIQUES COLLECTÉES:\n")
        
        metrics_found = {}
        for island in all_islands_data:
            for key, value in island.items():
                if value != 'N/A' and key not in ['code', 'scraped_at']:
                    metrics_found[key] = metrics_found.get(key, 0) + 1
        
        for metric, count in sorted(metrics_found.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(all_islands_data)) * 100
            status = "✅" if percentage > 80 else "⚠️" if percentage > 50 else "❌"
            print(f"   {status} {metric}: {count}/{len(all_islands_data)} ({percentage:.0f}%)")
        
        print(f"\n{'='*70}")
        print("🎉 Données prêtes pour l'analyse !")
        print("📂 Prochaine étape : Catégorisation et dashboard")
        print(f"{'='*70}\n")
        
        driver.quit()
        return all_islands_data
        
    except Exception as e:
        print(f"\n❌ Erreur globale: {str(e)}")
        driver.quit()
        return None

if __name__ == "__main__":
    # Scraper 30 îles pour commencer (test)
    # Une fois validé, passer à None pour tout scraper
    islands = scrape_all_islands_detailed(limit=30)