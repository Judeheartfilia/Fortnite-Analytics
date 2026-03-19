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

def scrape_500_islands():
    """Scrape 500 îles de fortnite.gg avec scroll infini"""
    
    print(f"\n{'='*70}")
    print(f"🚀 SCRAPING 500 ÎLES FORTNITE CREATIVE")
    print(f"🕐 Démarré à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    chrome_options = Options()
    # Mode headless pour aller plus vite
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("📡 Connexion à fortnite.gg/creative...")
        driver.get("https://fortnite.gg/creative")
        time.sleep(10)
        
        # Accepter cookies
        try:
            print("🍪 Acceptation des cookies...")
            driver.find_element(By.XPATH, "//button[contains(text(), 'Consent')]").click()
            time.sleep(5)
        except:
            print("⚠️  Pas de popup cookies")
        
        print("\n📜 Chargement des îles par scroll infini...")
        print("⏱️  Durée estimée : 5-10 minutes\n")
        
        islands_codes = set()
        no_new_islands_count = 0
        scroll_count = 0
        max_scrolls = 100  # Limiter à 100 scrolls pour 500 îles
        
        while len(islands_codes) < 500 and scroll_count < max_scrolls:
            # Scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Attendre le chargement
            
            scroll_count += 1
            
            # Extraire les codes
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            before_count = len(islands_codes)
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if href and 'code=' in href:
                        code_match = re.search(r'code=(\d{4}-\d{4}-\d{4})', href)
                        if code_match:
                            islands_codes.add(code_match.group(1))
                except:
                    continue
            
            after_count = len(islands_codes)
            new_islands = after_count - before_count
            
            if new_islands > 0:
                print(f"   Scroll {scroll_count:3d} | Total: {after_count:3d} îles | +{new_islands} nouvelles")
                no_new_islands_count = 0
            else:
                no_new_islands_count += 1
                print(f"   Scroll {scroll_count:3d} | Total: {after_count:3d} îles | Aucune nouvelle")
            
            # Si pas de nouvelles îles après 5 scrolls, on arrête
            if no_new_islands_count >= 5:
                print(f"\n⚠️  Pas de nouvelles îles après 5 scrolls, arrêt à {after_count} îles")
                break
        
        islands_codes = list(islands_codes)[:500]  # Limiter à 500
        
        print(f"\n{'='*70}")
        print(f"✅ {len(islands_codes)} codes d'îles récupérés")
        print(f"📊 Extraction des données détaillées...")
        print(f"{'='*70}\n")
        
        # Récupérer le HTML complet
        html = driver.page_source
        
        # Extraire les données pour chaque code
        islands_data = []
        
        for i, code in enumerate(islands_codes, 1):
            if i % 50 == 0:
                print(f"   Traité: {i}/{len(islands_codes)} îles...")
            
            # Chercher le nom et les stats dans le HTML
            pattern = f'(.{{1000}}){re.escape(code)}(.{{1000}})'
            matches = list(re.finditer(pattern, html, re.DOTALL | re.IGNORECASE))
            
            if matches:
                context = matches[0].group(0)
                
                # Extraire le nom (souvent avant ou après le code)
                name = "Unknown"
                
                # Chercher le texte du lien
                name_pattern = f'<a[^>]*href="[^"]*code={re.escape(code)}[^"]*"[^>]*>([^<]+)</a>'
                name_match = re.search(name_pattern, context)
                if name_match:
                    name = name_match.group(1).strip()
                
                # Extraire les stats (nombres avec K/M)
                numbers = re.findall(r'(\d+\.?\d*[KMB])', context, re.IGNORECASE)
                
                players = '0'
                favorites = '0'
                
                # Le plus gros nombre = joueurs, plus petit = favoris
                if numbers:
                    parsed = []
                    for num in numbers:
                        try:
                            if 'M' in num.upper():
                                val = float(num.upper().replace('M', '')) * 1_000_000
                            elif 'K' in num.upper():
                                val = float(num.upper().replace('K', '')) * 1_000
                            elif 'B' in num.upper():
                                val = float(num.upper().replace('B', '')) * 1_000_000_000
                            else:
                                val = float(num)
                            parsed.append((num, val))
                        except:
                            continue
                    
                    parsed.sort(key=lambda x: x[1], reverse=True)
                    
                    # Assigner intelligemment
                    for num, val in parsed:
                        if val >= 100_000 and players == '0':
                            players = num
                        elif val < 100_000 and val > 1000 and favorites == '0':
                            favorites = num
                
                island_info = {
                    'code': code,
                    'name': name,
                    'url': f'https://fortnite.gg/island?code={code}',
                    'stats': [players]
                }
                
                islands_data.append(island_info)
        
        driver.quit()
        
        # Sauvegarder
        os.makedirs('../data/raw', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'../data/raw/islands_500_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(islands_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ SCRAPING TERMINÉ")
        print(f"💾 Fichier: {filename}")
        print(f"📊 {len(islands_data)} îles sauvegardées")
        print(f"🕐 Terminé à {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Stats rapides
        with_names = len([i for i in islands_data if i['name'] != 'Unknown'])
        with_players = len([i for i in islands_data if i['stats'][0] != '0'])
        
        print(f"📈 STATISTIQUES:")
        print(f"   Noms extraits: {with_names}/{len(islands_data)} ({with_names/len(islands_data)*100:.0f}%)")
        print(f"   Stats joueurs: {with_players}/{len(islands_data)} ({with_players/len(islands_data)*100:.0f}%)")
        
        print(f"\n{'='*70}")
        print("📂 Prochaines étapes:")
        print("   1. py -3.9 clean_data.py (nettoyer les données)")
        print("   2. py -3.9 categorize_islands.py (catégoriser)")
        print("   3. py -3.9 update_dashboard.py (mettre à jour le dashboard)")
        print(f"{'='*70}\n")
        
        return islands_data
        
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
    islands = scrape_500_islands()