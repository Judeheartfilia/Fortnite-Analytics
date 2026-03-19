import json
import os
import glob

def clean_islands_data():
    """Nettoie et structure les données depuis le fichier le plus récent"""
    
    print(f"\n{'='*70}")
    print(f"🧹 NETTOYAGE ET STRUCTURATION DES DONNÉES")
    print(f"{'='*70}\n")
    
    # Trouver le fichier le plus récent
    import glob
    files = glob.glob('../data/raw/islands_*.json')
    
    if not files:
        print("❌ Aucun fichier trouvé dans data/raw/")
        return None
    
    latest_file = max(files, key=os.path.getctime)
    filename = os.path.basename(latest_file)
    
    print(f"📂 Fichier le plus récent détecté : {filename}")
    print(f"   Chemin : {latest_file}\n")
    
    # Charger les données brutes
    print("📂 Chargement des données...")
    with open(latest_file, 'r', encoding='utf-8') as f:
        raw_islands = json.load(f)
    print(f"✅ {len(raw_islands)} îles chargées\n")
    
    # Nettoyer et structurer
    cleaned_islands = []
    
    for island in raw_islands:
        # Extraire le nom propre (après le \n)
        name_raw = island.get('name', 'Unknown')
        
        if '\n' in name_raw:
            parts = name_raw.split('\n')
            favorites_str = parts[0].strip()
            name = parts[1].strip()
        else:
            name = name_raw
            favorites_str = '0'
        
        # Extraire les joueurs depuis stats[0]
        stats = island.get('stats', [])
        players_str = stats[0] if len(stats) > 0 else '0'
        
        # Convertir en nombres
        def parse_number(s):
            try:
                s = str(s).upper()
                if 'M' in s:
                    return int(float(s.replace('M', '')) * 1_000_000)
                elif 'K' in s:
                    return int(float(s.replace('K', '')) * 1_000)
                else:
                    return int(s.replace(',', ''))
            except:
                return 0
        
        players = parse_number(players_str)
        favorites = parse_number(favorites_str)
        
        cleaned_island = {
            'code': island['code'],
            'name': name,
            'url': island.get('url', ''),
            'players_24h': players,
            'players_display': players_str,
            'favorites': favorites,
            'favorites_display': favorites_str
        }
        
        cleaned_islands.append(cleaned_island)
        print(f"✅ {name[:45]:45} | Joueurs: {players_str:8} | Favoris: {favorites_str}")
    
    # Trier par nombre de joueurs
    cleaned_islands.sort(key=lambda x: x['players_24h'], reverse=True)
    
    # Sauvegarder
    os.makedirs('../data/processed', exist_ok=True)
    output_file = '../data/processed/islands_clean.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_islands, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print(f"✅ NETTOYAGE TERMINÉ")
    print(f"💾 Fichier: {output_file}")
    print(f"📊 Top 3:")
    for i, island in enumerate(cleaned_islands[:3], 1):
        print(f"   {i}. {island['name'][:40]} - {island['players_display']} joueurs")
    print(f"{'='*70}\n")
    
    return cleaned_islands

if __name__ == "__main__":
    islands = clean_islands_data()