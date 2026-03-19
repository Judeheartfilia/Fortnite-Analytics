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

def scrape_fortnite_main_page():
    """Scrape avec la méthode qui FONCTIONNAIT (extract_from_attributes)"""
    
    print(f"\n{'='*70}")
    print(f"🚀 FORTNITE CREATIVE ANALYTICS - SCRAPING OPTIMISÉ")
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
    
    try:
        print("📡 Connexion à fortnite.gg/creative...")
        driver.get("https://fortnite.gg/creative")
        time.sleep(10)
        
        # Accepter cookies
        try:
            print("🍪 Acceptation des cookies...")
            driver.find_element(By.XPATH, "//button[contains(text(), 'Consent')]").click()
            time.sleep(5)
            print("✅ Cookies acceptés")
        except:
            print("⚠️  Pas de popup cookies")
        
        # Scroll
        print("\n📜 Chargement du contenu...")
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        print("\n🔍 Extraction des îles...\n")
        
        # Chercher tous les liens avec code=
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        print(f"   {len(all_links)} liens analysés")
        
        islands_data = []
        
        for link in all_links:
            try:
                href = link.get_attribute('href')
                
                if href and 'code=' in href:
                    code_match = re.search(r'code=(\d{4}-\d{4}-\d{4})', href)
                    
                    if code_match:
                        code = code_match.group(1)
                        
                        # Extraire le texte visible du lien (nom de l'île)
                        name = link.text.strip()
                        
                        # Essayer de récupérer depuis l'image alt
                        try:
                            img = link.find_element(By.TAG_NAME, 'img')
                            img_alt = img.get_attribute('alt')
                            if img_alt and len(img_alt) > len(name):
                                name = img_alt
                        except:
                            pass
                        
                        if name and len(name) > 2:
                            island_info = {
                                'code': code,
                                'name': name,
                                'url': href,
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            islands_data.append(island_info)
                            print(f"   ✅ {name} ({code})")
                
            except Exception as e:
                continue
        
        # Supprimer doublons
        unique = {i['code']: i for i in islands_data}.values()
        islands_data = list(unique)
        
        print(f"\n✅ {len(islands_data)} îles uniques trouvées\n")
        
        # Enrichir avec les stats depuis le HTML
        print("📊 Enrichissement avec les métriques du HTML...\n")
        html = driver.page_source
        
        for island in islands_data:
            code = island['code']
            
            # Chercher un contexte large autour du code
            pattern = f'(.{{500}}){re.escape(code)}(.{{500}})'
            matches = list(re.finditer(pattern, html, re.DOTALL))
            
            if matches:
                context = matches[0].group(0)
                
                # Extraire TOUS les nombres avec K, M, B
                numbers = re.findall(r'(\d+\.?\d*[KMB])', context, re.IGNORECASE)
                
                # Nettoyer et convertir
                parsed_numbers = []
                for num in numbers:
                    try:
                        original = num
                        if 'M' in num.upper():
                            value = float(num.upper().replace('M', '')) * 1_000_000
                        elif 'K' in num.upper():
                            value = float(num.upper().replace('K', '')) * 1_000
                        elif 'B' in num.upper():
                            value = float(num.upper().replace('B', '')) * 1_000_000_000
                        else:
                            value = float(num)
                        
                        if value > 0:
                            parsed_numbers.append({
                                'original': original,
                                'value': value
                            })
                    except:
                        continue
                
                # Trier par valeur décroissante
                parsed_numbers.sort(key=lambda x: x['value'], reverse=True)
                
                # Assignment intelligent des métriques
                # Le plus gros nombre (>100K) = Joueurs 24h
                # Les petits nombres (<100K) = Favoris
                
                players = None
                favorites = None
                
                for num in parsed_numbers:
                    if num['value'] >= 100_000 and not players:
                        players = num['original']
                        island['players_24h'] = players
                    elif num['value'] < 100_000 and num['value'] > 1000 and not favorites:
                        favorites = num['original']
                        island['favorites'] = favorites
                
                # Chercher rétention (%)
                retention_match = re.search(r'(\d+)%', context)
                if retention_match:
                    island['retention'] = retention_match.group(1) + '%'
                
                # Chercher temps de jeu moyen (minutes)
                playtime_match = re.search(r'(\d+)\s*(?:min)', context, re.IGNORECASE)
                if playtime_match:
                    island['avg_playtime'] = playtime_match.group(1)
                
                print(f"✅ {island['name'][:45]}")
                if 'players_24h' in island:
                    print(f"   Joueurs 24h: {island['players_24h']}")
                if 'favorites' in island:
                    print(f"   Favoris: {island['favorites']}")
                if 'retention' in island:
                    print(f"   Rétention: {island['retention']}")
                if 'avg_playtime' in island:
                    print(f"   Temps moyen: {island['avg_playtime']} min")
                print()
        
        # Sauvegarder
        os.makedirs('../data/raw', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'../data/raw/islands_complete_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(islands_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ SCRAPING TERMINÉ")
        print(f"💾 Fichier: {filename}")
        print(f"📊 {len(islands_data)} îles scrapées")
        print(f"{'='*70}\n")
        
        # Statistiques finales
        print("📈 RÉSUMÉ DES MÉTRIQUES COLLECTÉES:\n")
        
        total = len(islands_data)
        with_players = len([i for i in islands_data if 'players_24h' in i])
        with_favorites = len([i for i in islands_data if 'favorites' in i])
        with_retention = len([i for i in islands_data if 'retention' in i])
        with_playtime = len([i for i in islands_data if 'avg_playtime' in i])
        
        def stat_line(name, count, total):
            pct = (count/total*100) if total > 0 else 0
            icon = "✅" if pct >= 80 else "⚠️" if pct >= 50 else "❌"
            return f"   {icon} {name}: {count}/{total} ({pct:.0f}%)"
        
        print(stat_line("Noms", len([i for i in islands_data if i.get('name')]), total))
        print(stat_line("Joueurs 24h", with_players, total))
        print(stat_line("Favoris", with_favorites, total))
        print(stat_line("Rétention", with_retention, total))
        print(stat_line("Temps moyen", with_playtime, total))
        
        print(f"\n{'='*70}")
        print("🎉 Données prêtes pour l'analyse !")
        print("📂 Prochaine étape : Catégorisation par genre/secteur")
        print(f"{'='*70}\n")
        
        driver.quit()
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
    islands = scrape_fortnite_main_page()