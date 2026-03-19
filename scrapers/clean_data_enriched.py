import json
import os
import glob

def format_display(n):
    """Formate un entier en nombre lisible : 958485 → '958 485', 2400000 → '2,4M'"""
    if n == 0:
        return 'N/A'
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n:,}".replace(',', ' ')  # espace comme séparateur milliers
    return str(n)


def parse_number(s):
    """Convertit 1.7M, 168K, 35.80% en nombres"""
    try:
        s = str(s).strip().upper()
        
        # Si c'est vide ou "N/A"
        if not s or s == 'N/A' or s == '0':
            return 0
        
        # Gérer les pourcentages
        if '%' in s:
            return float(s.replace('%', ''))
        
        # Gérer les nombres avec M, K, B
        if 'B' in s:
            return int(float(s.replace('B', '')) * 1_000_000_000)
        elif 'M' in s:
            return int(float(s.replace('M', '')) * 1_000_000)
        elif 'K' in s:
            return int(float(s.replace('K', '')) * 1_000)
        else:
            # Essayer de convertir directement
            return int(float(s.replace(',', '')))
    except:
        return 0

def clean_enriched_data():
    """Nettoie les données enrichies avec tous les KPIs"""
    
    print(f"\n{'='*70}")
    print(f"🧹 NETTOYAGE DES DONNÉES ENRICHIES")
    print(f"{'='*70}\n")
    
    # Trouver le fichier enrichi le plus récent
    files = glob.glob('../data/raw/islands_enriched_v2_*.json')
    if not files:
        files = glob.glob('../data/raw/islands_enriched_*.json')
    if not files:
        files = glob.glob('../data/raw/islands_v2_*.json')
    
    if not files:
        print("❌ Aucun fichier islands_enriched_*.json trouvé")
        print("   Lance d'abord : py -3.9 enrich_with_details.py")
        return None
    
    latest_file = max(files, key=os.path.getctime)
    filename = os.path.basename(latest_file)
    
    print(f"📂 Fichier trouvé : {filename}\n")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        raw_islands = json.load(f)
    
    print(f"✅ {len(raw_islands)} îles chargées\n")
    print("🔄 Nettoyage en cours...\n")
    
    cleaned_islands = []
    
    for island in raw_islands:
        # Nettoyer le nom
        name = island.get('name', 'Unknown')
        
        # Si format "XXK\nNOM"
        if '\n' in name:
            parts = name.split('\n')
            name = parts[-1].strip()
        
        # Extraire les valeurs brutes
        players_raw = island.get('players_24h', island.get('stats', ['N/A'])[0] if island.get('stats') else 'N/A')
        avg_ccu_raw = island.get('avg_ccu_24h', 'N/A')
        peak_ccu_raw = island.get('peak_ccu_24h', 'N/A')
        plays_raw = island.get('plays_24h', 'N/A')
        unique_players_raw = island.get('unique_players_24h', 'N/A')
        favorites_raw = island.get('favorites', 'N/A')
        recommendations_raw = island.get('recommendations', 'N/A')
        retention_d1_raw = island.get('retention_d1', 'N/A')
        retention_d7_raw = island.get('retention_d7', 'N/A')
        
        cleaned_island = {
            'code': island['code'],
            'name': name,
            'url': island.get('url', f"https://fortnite.gg/island?code={island['code']}"),
            
            # KPIs 24h - avec validation
            'players_24h': parse_number(players_raw),
            'players_24h_display': format_display(parse_number(players_raw)),

            'avg_ccu_24h': parse_number(avg_ccu_raw),
            'avg_ccu_24h_display': format_display(parse_number(avg_ccu_raw)),

            'peak_ccu_24h': parse_number(peak_ccu_raw),
            'peak_ccu_24h_display': format_display(parse_number(peak_ccu_raw)),

            # plays_24h = sessions_24h (fortnite.gg a renommé la métrique)
            'plays_24h': parse_number(island.get('sessions_24h', plays_raw)),
            'plays_24h_display': format_display(parse_number(island.get('sessions_24h', plays_raw))),

            'unique_players_24h': parse_number(unique_players_raw),
            'unique_players_24h_display': format_display(parse_number(unique_players_raw)),

            # Engagement
            'favorites': parse_number(favorites_raw),
            'favorites_display': format_display(parse_number(favorites_raw)),

            'recommendations': parse_number(recommendations_raw),
            'recommendations_display': format_display(parse_number(recommendations_raw)),
            
            # Temps de jeu
            'avg_playtime': island.get('avg_playtime', 'N/A'),
            'avg_session_time': island.get('avg_session_time', 'N/A'),
            
            # Rétention
            'retention_d1': parse_number(retention_d1_raw),
            'retention_d1_display': retention_d1_raw if retention_d1_raw != 'N/A' else 'N/A',
            
            'retention_d7': parse_number(retention_d7_raw),
            'retention_d7_display': retention_d7_raw if retention_d7_raw != 'N/A' else 'N/A',
            
            # Metadata
            'scraped_at': island.get('scraped_at', ''),

            # Nouveaux champs (scraper_v2)
            'created_date': island.get('created_date', None),
            'description': island.get('description', None),
            'tags': island.get('tags', []),
            'minutes_played': island.get('minutes_played', None),
            'total_playtime_24h': island.get('total_playtime_24h', None),
            'peak_ccu_alltime': parse_number(island.get('peak_ccu_alltime', 0)),
            'peak_ccu_alltime_display': format_display(parse_number(island.get('peak_ccu_alltime', 0))),
            'players_now': parse_number(island.get('players_now', 0)),
            'players_now_display': format_display(parse_number(island.get('players_now', 0))),
        }
        
        cleaned_islands.append(cleaned_island)
        
        # Affichage
        metrics = f"Players: {cleaned_island['players_24h_display']:8} | "
        metrics += f"Rét D1: {cleaned_island['retention_d1_display']:6} | "
        metrics += f"Rét D7: {cleaned_island['retention_d7_display']:6} | "
        metrics += f"Playtime: {cleaned_island['avg_playtime']}"
        
        print(f"✅ {name[:35]:35} | {metrics}")
    
    # Trier par joueurs 24h
    cleaned_islands.sort(key=lambda x: x['players_24h'], reverse=True)
    
    # Sauvegarder
    os.makedirs('../data/processed', exist_ok=True)
    output_file = '../data/processed/islands_clean.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_islands, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print(f"✅ NETTOYAGE TERMINÉ")
    print(f"💾 Fichier : {output_file}")
    print(f"{'='*70}\n")
    
    # Statistiques
    print("📊 STATISTIQUES DE COLLECTE :\n")
    
    stats = {
        'Players 24h': len([i for i in cleaned_islands if i['players_24h'] > 0]),
        'Peak CCU 24h': len([i for i in cleaned_islands if i['peak_ccu_24h'] > 0]),
        'Plays 24h': len([i for i in cleaned_islands if i['plays_24h'] > 0]),
        'Unique Players': len([i for i in cleaned_islands if i['unique_players_24h'] > 0]),
        'Recommendations': len([i for i in cleaned_islands if i['recommendations'] > 0]),
        'Rétention D1': len([i for i in cleaned_islands if i['retention_d1'] > 0]),
        'Rétention D7': len([i for i in cleaned_islands if i['retention_d7'] > 0]),
    }
    
    for metric, count in stats.items():
        pct = (count / len(cleaned_islands) * 100)
        icon = "✅" if pct > 80 else "⚠️" if pct > 50 else "❌"
        print(f"   {icon} {metric:20} : {count:3}/{len(cleaned_islands)} ({pct:5.1f}%)")
    
    print(f"\n📈 TOP 5 ÎLES PAR JOUEURS 24H :\n")
    for i, island in enumerate(cleaned_islands[:5], 1):
        print(f"   {i}. {island['name'][:40]:40} - {island['players_24h_display']:8} joueurs")
    
    print(f"\n📈 TOP 5 ÎLES PAR RÉTENTION D1 :\n")
    top_retention = sorted(cleaned_islands, key=lambda x: x['retention_d1'], reverse=True)[:5]
    for i, island in enumerate(top_retention, 1):
        print(f"   {i}. {island['name'][:40]:40} - {island['retention_d1_display']:6}")
    
    print(f"\n{'='*70}")
    print("📂 Prochaine étape :")
    print("   py -3.9 categorize_islands.py")
    print(f"{'='*70}\n")
    
    return cleaned_islands

if __name__ == "__main__":
    islands = clean_enriched_data()