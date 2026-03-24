import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json
from datetime import datetime
import os

def scrape_fortnite_gg_pages(max_pages=10):
    """Scrape fortnite.gg avec pagination (28 îles par page)"""
    
    print(f"\n{'='*70}")
    print(f"🚀 SCRAPING FORTNITE.GG AVEC PAGINATION")
    print(f"📄 Pages à scraper : {max_pages}")
    print(f"📊 Îles attendues : ~{max_pages * 28}")
    print(f"🕐 Démarré à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    driver = uc.Chrome(options=chrome_options, headless=True)
    
    all_islands = []
    
    try:
        for page in range(1, max_pages + 1):
            print(f"\n📄 PAGE {page}/{max_pages}")
            print("="*70)
            
            # URL avec pagination
            url = f"https://fortnite.gg/creative?page={page}" if page > 1 else "https://fortnite.gg/creative"
            
            driver.get(url)
            time.sleep(5)
            
            # Accepter cookies (première page seulement)
            if page == 1:
                consent_selectors = [
                    "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'CONSENT')]",
                    "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'ACCEPT')]",
                    "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'AGREE')]",
                    "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'OK')]",
                    "//*[contains(@class,'consent')]//button",
                    "//*[contains(@class,'cookie')]//button",
                    "//*[contains(@id,'accept')]",
                    "//*[contains(@class,'accept')]",
                ]
                clicked = False
                for selector in consent_selectors:
                    try:
                        btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        btn.click()
                        print("🍪 Cookies acceptés")
                        time.sleep(2)
                        clicked = True
                        break
                    except:
                        continue
                if not clicked:
                    print("⚠️  Pas de popup cookies détecté")
            
            print("📜 Chargement de la page...")
            time.sleep(3)
            
            # Extraire le HTML
            html = driver.page_source
            
            # Chercher tous les liens avec codes
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            page_islands = []
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    
                    if href and 'code=' in href:
                        code_match = re.search(r'code=(\d{4}-\d{4}-\d{4})', href)
                        
                        if code_match:
                            code = code_match.group(1)
                            
                            # Vérifier si déjà ajouté (éviter doublons)
                            if any(i['code'] == code for i in page_islands):
                                continue
                            
                            # Extraire le nom
                            name = link.text.strip()
                            
                            # Essayer alt de l'image
                            try:
                                img = link.find_element(By.TAG_NAME, 'img')
                                img_alt = img.get_attribute('alt')
                                if img_alt and len(img_alt) > len(name):
                                    name = img_alt
                            except:
                                pass
                            
                            if name and len(name) > 2:
                                page_islands.append({
                                    'code': code,
                                    'name': name,
                                    'url': href
                                })
                
                except:
                    continue
            
            # Enrichir avec stats depuis le HTML
            print(f"🔍 Enrichissement des {len(page_islands)} îles...\n")
            
            for island in page_islands:
                code = island['code']
                
                # Chercher contexte autour du code
                pattern = f'(.{{1000}}){re.escape(code)}(.{{1000}})'
                matches = list(re.finditer(pattern, html, re.DOTALL | re.IGNORECASE))
                
                if matches:
                    context = matches[0].group(0)
                    
                    # Extraire nombres (K, M)
                    numbers = re.findall(r'(\d+\.?\d*[KMB])', context, re.IGNORECASE)
                    
                    players = '0'
                    favorites = '0'
                    
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
                        
                        # Le plus gros = joueurs, plus petit = favoris
                        for num, val in parsed:
                            if val >= 100_000 and players == '0':
                                players = num
                            elif val < 100_000 and val > 1000 and favorites == '0':
                                favorites = num
                    
                    island['stats'] = [players]
                    
                    # Extraire favoris depuis le nom si format "XX.XK\nNOM"
                    if '\n' in island['name']:
                        parts = island['name'].split('\n')
                        if len(parts) == 2:
                            fav_candidate = parts[0].strip()
                            if 'K' in fav_candidate or 'M' in fav_candidate:
                                favorites = fav_candidate
                                island['name'] = parts[1].strip()
                    
                    print(f"✅ {island['name'][:40]:40} | Joueurs: {players:8} | Favoris: {favorites}")
            
            all_islands.extend(page_islands)
            
            print(f"\n📊 Total cumulé : {len(all_islands)} îles")
            
            # Pause entre les pages
            time.sleep(2)
        
        driver.quit()
        
        # Supprimer doublons finaux
        unique_islands = []
        seen_codes = set()
        
        for island in all_islands:
            if island['code'] not in seen_codes:
                unique_islands.append(island)
                seen_codes.add(island['code'])
        
        print(f"\n{'='*70}")
        print(f"✅ SCRAPING TERMINÉ")
        print(f"📊 Total îles : {len(unique_islands)} (après dédoublonnage)")
        print(f"🕐 Terminé à {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Sauvegarder
        os.makedirs('../data/raw', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'../data/raw/islands_pages_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(unique_islands, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Sauvegardé : {filename}\n")
        
        # Stats
        with_names = len([i for i in unique_islands if i.get('name') and i['name'] != 'Unknown'])
        with_stats = len([i for i in unique_islands if i.get('stats') and i['stats'][0] != '0'])
        
        print(f"📈 STATISTIQUES:")
        print(f"   Noms extraits : {with_names}/{len(unique_islands)} ({with_names/len(unique_islands)*100:.0f}%)")
        print(f"   Stats joueurs : {with_stats}/{len(unique_islands)} ({with_stats/len(unique_islands)*100:.0f}%)")
        
        print(f"\n{'='*70}")
        print("📂 Prochaines étapes:")
        print("   1. cd scrapers")
        print("   2. py -3.9 clean_data.py")
        print("   3. py -3.9 categorize_islands.py")
        print("   4. cd ../dashboard")
        print("   5. py -3.9 update_dashboard.py")
        print(f"{'='*70}\n")
        
        return unique_islands
        
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
    # Scraper 10 pages = ~280 îles
    # Modifier max_pages pour en avoir plus (ex: 20 pages = ~560 îles)
    islands = scrape_fortnite_gg_pages(max_pages=72)