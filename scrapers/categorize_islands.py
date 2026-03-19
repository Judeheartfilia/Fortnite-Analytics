"""
Catégorisation des îles Fortnite.
Utilise le nom + description + tags (quand disponibles).
Beaucoup plus de keywords pour réduire les "Autre".
"""

import json
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PROC   = os.path.join(SCRIPTS_DIR, '..', 'data', 'processed')


# ── 1. GENRES ──────────────────────────────────────────────────────────────────

GENRE_KEYWORDS = {
    'PvP': [
        '1v1', '2v2', '3v3', '4v4', 'pvp', 'vs', 'fight', 'fighter', 'battle',
        'war', 'wars', 'box fight', 'boxfight', 'realistics', 'realistic',
        'reload', 'gunfight', 'duel', 'arena fight', 'ffa', 'free for all',
        'team fight', 'combat', 'aim training', 'aim train',
    ],
    'Zone Wars': [
        'zone wars', 'zone war', 'zonewars', 'endgame', 'end game',
        'final zone', 'storm', 'arena',
    ],
    'Tycoon': [
        'tycoon', 'empire', 'business', 'idle', 'clicker', 'factory',
        'shop', 'store', 'economy', 'money', 'cash', 'rich', 'mogul',
        'magnate', 'entrepreneur',
    ],
    'Deathrun': [
        'deathrun', 'death run', 'parkour', 'obby', 'obstacle', 'course',
        'dropper', 'drop', 'jumper', 'platform', 'platformer',
    ],
    'Horror': [
        'horror', 'scary', 'fear', 'fnaf', 'granny', 'slenderman',
        'haunted', 'nightmare', 'creepy', 'evil', 'demon', 'ghost',
        'monster', 'killer', 'murderer', 'asylum', 'possessed',
    ],
    'Escape Room': [
        'escape', 'escape room', 'prison break', 'jailbreak', 'breakout',
        'trapped', 'locked', 'get out', 'flee',
    ],
    'Tsunami / Disaster': [
        'tsunami', 'flood', 'disaster', 'earthquake', 'volcano', 'lava',
        'meteor', 'apocalypse',
    ],
    'Survival': [
        'survival', 'survive', 'survivor', 'last man', 'apocalypse',
        'stranded', 'wild', 'wilderness',
    ],
    'Zombie': [
        'zombie', 'zombies', 'undead', 'infected', 'horde', 'walker',
        'dead', 'brain',
    ],
    'Roleplay': [
        'roleplay', 'role play', ' rp ', 'rp:', 'city life', 'town',
        'life sim', 'life simulator', 'high school', 'school life',
        'hospital', 'military', 'police', 'firefighter', 'restaurant rp',
    ],
    'Simulator': [
        'simulator', 'simulation', 'driving', 'farming', 'cooking',
        'fishing simulator', 'flight', 'space sim',
    ],
    'Racing': [
        'racing', 'race', 'drift', 'car race', 'kart', 'f1', 'nascar',
        'rally', 'speedway', 'circuit', 'track',
    ],
    'Party Game': [
        'party', 'mini game', 'mini-game', 'minigame', 'fall guys',
        'fall game', 'among us', 'among', 'trivia', 'quiz',
        'game show', 'show game',
    ],
    'Social / Hangout': [
        'hangout', 'chill', 'vibe', 'social', 'hub', 'lounge',
        'meet', 'meetup', 'concert', 'club', 'bar', 'disco',
    ],
    'Edit Course': [
        'edit course', 'edit', 'piece control', 'build fight', 'box pvp',
        'mechanical', 'mechanics', 'keybind', 'warmup',
    ],
    'Mini-jeux': [
        'murder mystery', 'prop hunt', 'prop & hunt', 'hide and seek',
        'hide & seek', 'tag', 'dodgeball', 'fishing', 'pit',
        'sword fight', 'knife', 'skywars', 'sky wars',
    ],
    'Bed Wars': [
        'bed wars', 'bedwars', 'bed war',
    ],
    'Red vs Blue': [
        'red vs blue', 'red v blue', 'rvb', 'red blue',
    ],
    'Roguelike / Dungeon': [
        'roguelike', 'rogue', 'dungeon', 'dungeon crawler', 'rpg',
        'adventure', 'quest', 'raid', 'boss fight', 'boss rush',
    ],
    'Battle Royale': [
        'battle royale', 'br mode', 'last player', 'last one standing',
        '100 players', 'solos', 'squads', 'duos',
    ],
    'Creative / Sandbox': [
        'sandbox', 'creative', 'build', 'builder', 'architect',
        'freeplay', 'free play', 'open world',
    ],
}

# ── 2. MÉCANIQUES ──────────────────────────────────────────────────────────────

MECHANICS_KEYWORDS = {
    'Skill-based': [
        '1v1', 'aim', 'edit', 'piece control', 'build fight', 'realistic',
        'mechanical', 'high skill', 'competitive',
    ],
    'Progression': [
        'tycoon', 'level', 'upgrade', 'unlock', 'roguelike', 'xp',
        'rank', 'prestige', 'season pass', 'idle',
    ],
    'Combat': [
        'fight', 'pvp', 'war', 'battle', 'gun', 'shoot', 'shooter',
        'sniper', 'rifle', 'grenade', 'duel',
    ],
    'Exploration': [
        'open world', 'map', 'explore', 'adventure', 'quest', 'discover',
    ],
    'Coop': [
        'coop', 'co-op', 'team', '2v2', '3v3', '4v4', 'squad', 'duo',
    ],
    'Competitive': [
        'ranked', 'competitive', 'zone wars', 'arena', 'tournament',
        'championship', 'league',
    ],
    'Social': [
        'party', 'hangout', 'roleplay', 'social', 'club', 'meet',
    ],
    'Speedrun': [
        'deathrun', 'parkour', 'race', 'speedrun', 'timer', 'fastest',
        'dropper', 'dropper',
    ],
    'Strategy': [
        'strategy', 'tactics', 'bed wars', 'tower', 'defend', 'base',
    ],
    'Horror / Tension': [
        'horror', 'scary', 'escape', 'survive', 'hide', 'stealth',
    ],
    'RNG / Luck': [
        'rng', 'random', 'luck', 'loot', 'gacha', 'spin',
    ],
    'Creative / Building': [
        'creative', 'build', 'sandbox', 'architect',
    ],
}

# ── 3. MARQUES ─────────────────────────────────────────────────────────────────

BRANDS = {
    # Mode
    'Nike':        ['nike'],
    'Adidas':      ['adidas'],
    'Jordan':      ['jordan'],
    'Balenciaga':  ['balenciaga'],
    'Gucci':       ['gucci'],
    'Louis Vuitton': ['louis vuitton', 'lv'],
    'Supreme':     ['supreme'],
    # Auto
    'Ferrari':     ['ferrari'],
    'Lamborghini': ['lambo', 'lamborghini'],
    'McLaren':     ['mclaren'],
    'Tesla':       ['tesla'],
    'BMW':         ['bmw'],
    'Mercedes':    ['mercedes'],
    'Bugatti':     ['bugatti'],
    # Food
    'Coca-Cola':   ['coca-cola', 'coca cola', 'coke'],
    'Pepsi':       ['pepsi'],
    'McDonalds':   ['mcdonalds', "mcdonald's"],
    'Burger King': ['burger king'],
    'KFC':         ['kfc'],
    'Wendys':      ["wendy's", 'wendys'],
    'Taco Bell':   ['taco bell'],
    'Starbucks':   ['starbucks'],
    'Red Bull':    ['red bull', 'redbull'],
    'Monster':     ['monster energy'],
    'Doritos':     ['doritos'],
    # Médias
    'Netflix':     ['netflix'],
    'Disney':      ['disney'],
    'Marvel':      ['marvel', 'avengers', 'spider-man', 'spiderman', 'iron man'],
    'DC':          ['batman', 'superman', 'dc comics', 'dc universe'],
    'Star Wars':   ['star wars', 'jedi', 'sith'],
    'Stranger Things': ['stranger things'],
    'Squid Game':  ['squid game'],
    'One Piece':   ['one piece'],
    'Naruto':      ['naruto'],
    # Sport
    'NBA':         ['nba'],
    'NFL':         ['nfl'],
    'FIFA':        ['fifa'],
    'Formula 1':   ['formula 1', 'formula1', 'f1 race'],
    'WWE':         ['wwe'],
    'Fortnite IP': ['chapter', 'og fortnite', 'original fortnite'],
}

BRAND_SECTORS = {
    'Mode / Fashion':         ['Nike', 'Adidas', 'Jordan', 'Balenciaga', 'Gucci', 'Louis Vuitton', 'Supreme'],
    'Sport / Automobile':     ['Ferrari', 'Lamborghini', 'McLaren', 'Tesla', 'BMW', 'Mercedes', 'Bugatti', 'NBA', 'NFL', 'FIFA', 'Formula 1', 'WWE'],
    'Food / Boisson':         ['Coca-Cola', 'Pepsi', 'McDonalds', 'Burger King', 'KFC', 'Wendys', 'Taco Bell', 'Starbucks', 'Red Bull', 'Monster', 'Doritos'],
    'Médias / Entertainment': ['Netflix', 'Disney', 'Marvel', 'DC', 'Star Wars', 'Stranger Things', 'Squid Game', 'One Piece', 'Naruto'],
}

# ── 4. SECTEURS ────────────────────────────────────────────────────────────────

SECTOR_KEYWORDS = {
    'Mode / Fashion':         ['fashion', 'style', 'clothing', 'streetwear', 'outfit', 'skin', 'drip'],
    'Sport / Automobile':     ['car', 'racing', 'drift', 'formula', 'nascar', 'sport', 'football', 'soccer', 'basketball', 'tennis'],
    'Food / Boisson':         ['restaurant', 'food', 'cafe', 'pizza', 'burger', 'coffee', 'drink', 'kitchen', 'chef'],
    'Médias / Entertainment': ['show', 'tv', 'series', 'movie', 'film', 'concert', 'music', 'cinema', 'theater'],
    'Ville / Lieu':           ['city', 'ville', 'museum', 'hotel', 'park', 'mall', 'center', 'downtown', 'paris', 'new york', 'london'],
    'Banque / Finance / Assurance': ['bank', 'insurance', 'assurance', 'credit', 'finance', 'crypto', 'nft'],
    'Éducation':              ['school', 'university', 'college', 'education', 'learn', 'classroom', 'campus'],
    'Santé':                  ['health', 'hospital', 'medical', 'doctor', 'clinic', 'pharmacy'],
    'Gaming Pure':            [],
}


def get_search_text(island):
    """Agrège nom + description + tags en un texte de recherche minuscules."""
    parts = [island.get('name', '')]
    if island.get('description'):
        parts.append(island['description'])
    if island.get('tags'):
        parts.extend(island['tags'])
    return ' '.join(parts).lower()


def match_keywords(text, keywords):
    return any(kw in text for kw in keywords)


def categorize_islands():
    print(f"\n{'='*60}")
    print(f"CATEGORISATION DES ILES")
    print(f"{'='*60}\n")

    with open(os.path.join(DATA_PROC, 'islands_clean.json'), 'r', encoding='utf-8') as f:
        islands = json.load(f)

    print(f"{len(islands)} iles chargees\n")

    for island in islands:
        text = get_search_text(island)

        # ── Genre ──────────────────────────────────────────────────────────
        island['genre'] = [
            genre for genre, kws in GENRE_KEYWORDS.items()
            if match_keywords(text, kws)
        ]
        if not island['genre']:
            island['genre'] = ['Autre']

        # ── Mécaniques ─────────────────────────────────────────────────────
        island['mechanics'] = [
            mec for mec, kws in MECHANICS_KEYWORDS.items()
            if match_keywords(text, kws)
        ]
        if not island['mechanics']:
            island['mechanics'] = ['Autre']

        # ── Marque & Secteur ───────────────────────────────────────────────
        island['brand'] = None
        island['sector'] = 'Gaming Pure'

        for brand, kws in BRANDS.items():
            if match_keywords(text, kws):
                island['brand'] = brand
                for sector, brand_list in BRAND_SECTORS.items():
                    if brand in brand_list:
                        island['sector'] = sector
                        break
                break

        if island['sector'] == 'Gaming Pure':
            for sector, kws in SECTOR_KEYWORDS.items():
                if kws and match_keywords(text, kws):
                    island['sector'] = sector
                    break

    # Sauvegarder
    out = os.path.join(DATA_PROC, 'islands_categorized.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(islands, f, indent=2, ensure_ascii=False)

    # ── Statistiques ───────────────────────────────────────────────────────
    total = len(islands)

    genre_counts = {}
    for isl in islands:
        for g in isl['genre']:
            genre_counts[g] = genre_counts.get(g, 0) + 1

    mec_counts = {}
    for isl in islands:
        for m in isl['mechanics']:
            mec_counts[m] = mec_counts.get(m, 0) + 1

    sector_counts = {}
    for isl in islands:
        s = isl['sector']
        sector_counts[s] = sector_counts.get(s, 0) + 1

    brands_found = [i for i in islands if i.get('brand')]

    print("GENRES:")
    for g, c in sorted(genre_counts.items(), key=lambda x: -x[1])[:15]:
        bar = '#' * (c * 20 // total)
        autre = ' ← a classifier' if g == 'Autre' else ''
        print(f"  {g:25} {c:3}  {bar}{autre}")

    print("\nMECANIQUES:")
    for m, c in sorted(mec_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {m:25} {c:3}")

    print("\nSECTEURS:")
    for s, c in sorted(sector_counts.items(), key=lambda x: -x[1]):
        print(f"  {s:35} {c:3}")

    if brands_found:
        print(f"\nMARQUES ({len(brands_found)}):")
        for isl in brands_found:
            print(f"  {isl['brand']:20} {isl['name'][:40]}")

    autre_genre = genre_counts.get('Autre', 0)
    autre_mec   = mec_counts.get('Autre', 0)
    print(f"\nRESULTAT:")
    print(f"  Genre 'Autre'    : {autre_genre}/{total} ({autre_genre/total*100:.0f}%)")
    print(f"  Mecanique 'Autre': {autre_mec}/{total} ({autre_mec/total*100:.0f}%)")
    print(f"\nFichier: {os.path.basename(out)}")
    print(f"\nProchaine etape:")
    print(f"  python ../dashboard/update_dashboard.py")
    print(f"{'='*60}\n")

    return islands


if __name__ == "__main__":
    categorize_islands()
