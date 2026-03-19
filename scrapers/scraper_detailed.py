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

def extract_stat(html, label):
    """Extrait une stat depuis le HTML avec son label"""
    # Chercher le label suivi d'un nombre
    patterns = [
        f'{label}[^\\d]*(\\d+\\.?\\d*[KMB]?)',
        f'{label}.*?(\\d+\\.?\\d*[KMB]?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
    return 'N/A'

def scrape_island_detailed(driver, code):
    """Scrape tous les détails d'une île depuis sa page dédiée"""
    
    url = f"https://fortnite.gg/island?code={code}"
    
    try:
        driver.get(url)
        time.sleep(4)  # Attendre chargement complet
        
        html = driver.page_source
        
        # Extraire le nom
        title_match = re.search(r'<title>(.*?)</title>', html)
        name = title_match.group(1).replace(' - Fortnite.GG', '').strip() if title_match else 'Unknown'
        
        island_data = {
            'code': code,
            'name': name,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            
            # 24h Overview
            'players_24h': extract_stat(html, '(?:Players|PLAYERS)'),
            'avg_ccu_24h': extract_stat(html, 'Avg CCU'),
            'peak_ccu_24h': extract_stat(html, 'Peak CCU'),
            'plays_24h': extract_stat(html, 'Plays'),
            'playtime_24h': extract_stat(html, 'Playtime'),
            'unique_players_24h': extract_stat(html, 'Unique Players'),
            
            # Engagement
            'favorites': extract_stat(html, 'Favorites'),
            'recommendations': extract_stat(html, 'Recommendations'),
            'avg_playtime': extract_stat(html, 'Average Playtime'),
            'avg_session_time': extract_stat(html, 'Average Session Time'),
            
            # Rétention
            'retention_d1': extract_stat(html, 'Day 1 Retention'),
            'retention_d7': extract_stat(html, 'Day 7 Retention'),
            
            # All-time
            'plays_alltime': extract_stat(html, 'ALL-TIME.*?Plays'),
            'favorites_alltime': extract_stat(html, 'ALL-TIME.*?Favorites'),
        }
        
        # Chercher la date de création
        date_patterns = [
            r'Created[^\\d]*(\\d{1,2}/\\d{1,2}/\\d{4})',
            r'Published[^\\d]*(\\d{1,2}/\\d{1,2}/\\d{4})',
            r'Added[^\\d]*(\\d{1,2}/\\d{1,2}/\\d{4})',
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, html, re.IGNORECASE)
            if date_match:
                island_data['created_date'] = date_match.group(1)
                break
        
        return island_data
        
    except Exception as e:
        print(f"      ❌ Erreur: {str(e)}")
        return None

def scrape_all_detailed(max_pages=10):
    """Scrape fortnite.gg avec pagination puis détails de chaque île"""
    
    print(f"\n{'='*70}")
    print(f"🚀 SCRAPING DÉTAILLÉ FORTNITE.GG")
    print(f"📄 Pages : {max_pages} (~{max_pages * 28} îles)")
    print(f"⏱️  Durée estimée : {max_pages * 28 * 5 / 60:.0f} minutes")
    print(f"🕐 Démarré à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Désactivé pour debug
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # ÉTAPE 1 : Collecter tous les codes
    print("📋 ÉTAPE 1 : Collecte des codes\n")
    
    all_codes = set()
    
    try:
        for page in range(1, max_pages + 1):
            url = f"https://fortnite.gg/creative?page={page}" if page > 1 else "https://fortnite.gg/creative"
            
            driver.get(url)
            time.sleep(10)
            
            if page == 1:
                try:
                    driver.find_element(By.XPATH, "//button[contains(text(), 'Consent')]").click()
                    time.sleep(3)
                except:
                    pass
            
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            page_codes = set()
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if href and 'code=' in href:
                        code_match = re.search(r'code=(\\d{4}-\\d{4}-\\d{4})', href)
                        if code_match:
                            page_codes.add(code_match.group(1))
                except:
                    continue
            
            all_codes.update(page_codes)
            print(f"   Page {page:2d} : {len(page_codes):2d} codes | Total : {len(all_codes):3d}")
            
            time.sleep(2)
        
        codes_list = sorted(list(all_codes))
        
        print(f"\n✅ {len(codes_list)} codes uniques collectés")
        
        # ÉTAPE 2 : Scraper les détails
        print(f"\n{'='*70}")
        print(f"📊 ÉTAPE 2 : Scraping détaillé de chaque île")
        print(f"{'='*70}\n")
        
        all_islands = []
        
        for i, code in enumerate(codes_list, 1):
            print(f"[{i:3d}/{len(codes_list)}] {code}", end=" ")
            
            island_data = scrape_island_detailed(driver, code)
            
            if island_data:
                all_islands.append(island_data)
                print(f"✅ {island_data['name'][:40]}")
            else:
                print(f"❌ Échec")
            
            # Pause pour éviter rate limiting
            if i % 10 == 0:
                print(f"      ⏸️  Pause de 5 secondes...")
                time.sleep(5)
            else:
                time.sleep(2)
        
        driver.quit()
        
        # Sauvegarder
        os.makedirs('../data/raw', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'../data/raw/islands_detailed_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_islands, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ SCRAPING TERMINÉ")
        print(f"💾 Fichier : {filename}")
        print(f"📊 {len(all_islands)} îles avec KPIs complets")
        print(f"🕐 Terminé à {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Stats
        stats = {
            'players_24h': len([i for i in all_islands if i.get('players_24h') != 'N/A']),
            'retention_d1': len([i for i in all_islands if i.get('retention_d1') != 'N/A']),
            'retention_d7': len([i for i in all_islands if i.get('retention_d7') != 'N/A']),
            'avg_playtime': len([i for i in all_islands if i.get('avg_playtime') != 'N/A']),
        }
        
        print("📈 TAUX DE COLLECTE :")
        for metric, count in stats.items():
            pct = (count / len(all_islands) * 100) if all_islands else 0
            print(f"   {metric}: {count}/{len(all_islands)} ({pct:.0f}%)")
        
        print(f"\n{'='*70}")
        print("📂 Prochaines étapes :")
        print("   1. py -3.9 clean_data_detailed.py")
        print("   2. py -3.9 categorize_islands.py")
        print("   3. cd ../dashboard && py -3.9 update_dashboard.py")
        print(f"{'='*70}\n")
        
        return all_islands
        
    except Exception as e:
        print(f"\n❌ Erreur globale: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            driver.quit()
        except:
            pass
        return None

if __name__ == "__main__":
    # Scraper 5 pages pour commencer (test)
    # Augmenter à 10-20 pages une fois validé
    islands = scrape_all_detailed(max_pages=5)