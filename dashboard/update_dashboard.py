import json
from datetime import datetime

def update_dashboard():
    """Génère le dashboard HTML ultra-complet avec toutes les fonctionnalités"""
    
    print(f"\n{'='*70}")
    print(f"🎨 GÉNÉRATION DU DASHBOARD ULTRA-COMPLET")
    print(f"{'='*70}\n")
    
    # Charger les données catégorisées
    print("📂 Chargement des données...")
    with open('../data/processed/islands_categorized.json', 'r', encoding='utf-8') as f:
        islands = json.load(f)
    
    print(f"✅ {len(islands)} îles chargées\n")
    
    # Convertir en format JavaScript
    islands_js = []
    for island in islands:
        islands_js.append({
            'name': island['name'],
            'code': island['code'],
            
            # KPIs 24h
            'players': island.get('players_24h', 0),
            'players_display': island.get('players_24h_display') or island.get('players_display', 'N/A'),

            'unique_players': island.get('unique_players_24h', 0),
            'unique_players_display': island.get('unique_players_24h_display', 'N/A'),

            'peak_ccu': island.get('peak_ccu_24h', 0),
            'peak_ccu_display': island.get('peak_ccu_24h_display', 'N/A'),

            'peak_ccu_alltime': island.get('peak_ccu_alltime', 0),
            'peak_ccu_alltime_display': island.get('peak_ccu_alltime_display', 'N/A'),

            'players_now': island.get('players_now', 0),
            'players_now_display': island.get('players_now_display', 'N/A'),

            # Sessions (= plays sur fortnite.gg)
            'plays': island.get('plays_24h', 0),
            'plays_display': island.get('plays_24h_display', 'N/A'),

            # Engagement
            'favorites': island.get('favorites', 0),
            'favorites_display': island.get('favorites_display', 'N/A'),

            'recommendations': island.get('recommendations', 0),
            'recommendations_display': island.get('recommendations_display', 'N/A'),

            # Rétention
            'retention_d1': island.get('retention_d1', 0),
            'retention_d1_display': island.get('retention_d1_display', 'N/A'),

            'retention_d7': island.get('retention_d7', 0),
            'retention_d7_display': island.get('retention_d7_display', 'N/A'),

            # Temps de jeu
            'avg_playtime': island.get('avg_playtime', 'N/A'),
            'avg_session_time': island.get('avg_session_time', 'N/A'),
            'minutes_played': island.get('minutes_played', 'N/A'),

            # Metadata
            'created_date': island.get('created_date', 'N/A'),
            'genre': island['genre'],
            'mechanics': island['mechanics'],
            'sector': island['sector'],
            'brand': island.get('brand'),
            'tags': island.get('tags', [])
        })
    
    islands_json = json.dumps(islands_js, ensure_ascii=False, indent=8)
    
    print("📊 Données converties en JavaScript")
    print(f"   {len(islands_js)} îles prêtes\n")
    
    # Générer le HTML ultra-complet
    html_content = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fortnite Creative Analytics - Pro Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --bg-primary: #0d0d17;
            --bg-secondary: #13131f;
            --bg-card: #1c1c2e;
            --accent-purple: #7b2fbe;
            --accent-purple-light: #9b47e0;
            --accent-cyan: #00c8ff;
            --accent-green: #00c896;
            --text-primary: #ffffff;
            --text-secondary: #8b95a5;
            --border-color: #2a2a3e;
            --glow: 0 0 20px rgba(123, 47, 190, 0.3);
        }}

        [data-theme="light"] {{
            --bg-primary: #f4f4f8;
            --bg-secondary: #ffffff;
            --bg-card: #ffffff;
            --accent-purple: #6d28d9;
            --accent-purple-light: #7c3aed;
            --accent-cyan: #0284c7;
            --accent-green: #059669;
            --text-primary: #0f0f1a;
            --text-secondary: #64748b;
            --border-color: #e2e2f0;
            --glow: none;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            transition: all 0.3s;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: 280px 1fr;
            min-height: 100vh;
        }}

        .sidebar {{
            background: var(--bg-secondary);
            padding: 30px 20px;
            border-right: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }}
        
        .logo {{
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 8px;
            background: linear-gradient(90deg, var(--accent-purple-light), var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .filter-section {{
            margin-bottom: 30px;
        }}
        
        .filter-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .filter-select {{
            width: 100%;
            padding: 12px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 14px;
            cursor: pointer;
        }}
        
        .search-input {{
            width: 100%;
            padding: 12px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 14px;
        }}
        
        .theme-toggle {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            cursor: pointer;
        }}
        
        .toggle-switch {{
            position: relative;
            width: 48px;
            height: 24px;
            background: var(--border-color);
            border-radius: 12px;
        }}
        
        .toggle-switch.active {{
            background: var(--accent-purple);
        }}
        
        .toggle-switch::after {{
            content: '';
            position: absolute;
            width: 18px;
            height: 18px;
            background: white;
            border-radius: 50%;
            top: 3px;
            left: 3px;
            transition: all 0.3s;
        }}
        
        .toggle-switch.active::after {{
            left: 27px;
        }}
        
        .export-btn {{
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-purple-light));
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 10px;
            box-shadow: var(--glow);
        }}

        .export-btn:hover {{ opacity: 0.85; }}
        
        .main-content {{
            padding: 30px 40px;
            overflow-y: auto;
            max-height: 100vh;
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        
        .header p {{
            color: var(--text-secondary);
            font-size: 14px;
        }}
        
        .insights-section {{
            background: linear-gradient(135deg, var(--accent-purple), #3b1a6e);
            border: 1px solid rgba(123, 47, 190, 0.4);
            border-radius: 12px;
            padding: 24px;
            margin: 30px 0;
            color: white;
            box-shadow: var(--glow);
        }}
        
        .insights-title {{
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 16px;
        }}
        
        .insight-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 10px;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            transition: transform 0.2s, box-shadow 0.2s;
            position: relative;
            overflow: hidden;
        }}
        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: var(--card-accent, linear-gradient(90deg, var(--accent-purple), var(--accent-cyan)));
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 0 24px var(--card-glow, rgba(123,47,190,0.35)), 0 0 60px var(--card-glow, rgba(123,47,190,0.12));
        }}
        .kpi-card:nth-child(1) {{ --card-accent: linear-gradient(90deg,#7b2fbe,#9b47e0); --card-glow: rgba(123,47,190,0.4); }}
        .kpi-card:nth-child(2) {{ --card-accent: linear-gradient(90deg,#00c8ff,#0080ff); --card-glow: rgba(0,200,255,0.4); border-color: rgba(0,200,255,0.15); }}
        .kpi-card:nth-child(3) {{ --card-accent: linear-gradient(90deg,#00c896,#00a080); --card-glow: rgba(0,200,150,0.4); border-color: rgba(0,200,150,0.15); }}
        .kpi-card:nth-child(4) {{ --card-accent: linear-gradient(90deg,#f59e0b,#ef4444); --card-glow: rgba(245,158,11,0.4); border-color: rgba(245,158,11,0.15); }}
        .kpi-card:nth-child(5) {{ --card-accent: linear-gradient(90deg,#ec4899,#8b5cf6); --card-glow: rgba(236,72,153,0.4); border-color: rgba(236,72,153,0.15); }}
        
        .kpi-label {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }}
        
        .kpi-value {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        
        .kpi-change {{
            font-size: 12px;
            color: var(--accent-green);
        }}
        
        .charts-grid {{
            margin-bottom: 30px;
            max-width: 50%;
            margin-left: auto;
            margin-right: auto;
        }}

        .chart-tabs {{
            display: flex;
            gap: 4px;
            border-bottom: 2px solid var(--border-color);
        }}

        .chart-tab {{
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 500;
            color: var(--text-secondary);
            cursor: pointer;
            border: none;
            background: none;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all 0.2s;
            font-family: 'Inter', sans-serif;
        }}

        .chart-tab:hover {{ color: var(--text-primary); }}

        .chart-tab.active {{
            color: var(--accent-cyan);
            border-bottom-color: var(--accent-cyan);
        }}

        .chart-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-top: none;
            border-radius: 0 0 12px 12px;
            padding: 24px;
            display: none;
            box-shadow: 0 0 30px rgba(123,47,190,0.12);
        }}

        .chart-card.active {{ display: block; }}

        .chart-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
        }}
        
        .table-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 0 40px rgba(0,200,255,0.06), 0 0 80px rgba(123,47,190,0.08);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            padding: 14px 16px;
            text-align: left;
            font-size: 12px;
            text-transform: uppercase;
            color: var(--text-secondary);
            border-bottom: 1px solid var(--border-color);
            cursor: pointer;
        }}
        
        td {{
            padding: 14px 16px;
            font-size: 14px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            background: rgba(123, 47, 190, 0.18);
            color: var(--accent-purple-light);
            margin-right: 4px;
            border: 1px solid rgba(123, 47, 190, 0.3);
        }}
        
        .rank {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border-radius: 6px;
            background: var(--bg-secondary);
            font-weight: 600;
        }}
        
        .rank.top {{
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            color: #000;
        }}
        
        .code {{
            font-family: monospace;
            font-size: 12px;
            color: var(--text-secondary);
        }}

        th.sortable {{
            user-select: none;
            white-space: nowrap;
        }}
        th.sortable:hover {{
            color: var(--text-primary);
        }}
        th.sort-asc::after {{
            content: ' ↑';
            color: var(--accent-cyan);
        }}
        th.sort-desc::after {{
            content: ' ↓';
            color: var(--accent-cyan);
        }}

        .refresh-btn {{
            padding: 8px 18px;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-purple-light));
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 12px;
        }}
        .refresh-btn:hover {{
            opacity: 0.85;
        }}

        .brand-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            background: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <aside class="sidebar">
            <div class="logo">🎮 Fortnite Analytics</div>

            <nav style="display:flex;flex-direction:column;gap:6px;margin-bottom:28px;">
                <a href="analytics_dashboard.html" style="padding:8px 12px;border-radius:8px;font-size:14px;color:var(--accent-blue);font-weight:600;background:var(--bg-card);text-decoration:none;">📊 Dashboard</a>
                <a href="recommandations.html" style="padding:8px 12px;border-radius:8px;font-size:14px;color:var(--text-secondary);text-decoration:none;">💡 Recommandations</a>
            </nav>

            <div class="filter-section">
                <div class="filter-label">🔍 Recherche</div>
                <input type="text" id="searchInput" class="search-input" placeholder="Rechercher..." oninput="applyFilters()">
            </div>
            
            <div class="filter-section">
                <div class="filter-label">Genre</div>
                <select id="genreFilter" class="filter-select" onchange="applyFilters()">
                    <option value="all">Tous</option>
                </select>
            </div>
            
            <div class="filter-section">
                <div class="filter-label">Mécanique</div>
                <select id="mechanicFilter" class="filter-select" onchange="applyFilters()">
                    <option value="all">Toutes</option>
                </select>
            </div>
            
            <div class="filter-section">
                <div class="filter-label">Secteur</div>
                <select id="sectorFilter" class="filter-select" onchange="applyFilters()">
                    <option value="all">Tous</option>
                </select>
            </div>
            
            <div class="filter-section">
                <div class="filter-label">Tri</div>
                <select id="sortBy" class="filter-select" onchange="applyFilters()">
                    <option value="players">Joueurs ↓</option>
                    <option value="name">Nom A-Z</option>
                </select>
            </div>
            
            <div class="filter-section">
                <div class="filter-label">Thème</div>
                <div class="theme-toggle" onclick="toggleTheme()">
                    <span>☀️ / 🌙</span>
                    <div class="toggle-switch" id="themeSwitch"></div>
                </div>
            </div>
            
            <div class="filter-section">
                <button class="export-btn" onclick="exportToExcel()">📥 Excel</button>
            </div>
        </aside>
        
        <main class="main-content">
            <div class="header">
                <h1>Creative Analytics Dashboard</h1>
                <p>Analyse des performances Fortnite Creative</p>
                <p style="color: var(--text-secondary); font-size: 12px; margin-top: 8px;">
                    🕐 Mis à jour le <span id="lastUpdated"></span>
                </p>
                <button class="refresh-btn" onclick="location.reload()">🔄 Rafraîchir</button>
            </div>
            
            <div class="insights-section" id="insightsSection"></div>
            <div class="kpi-grid" id="kpiGrid"></div>
            
            <div class="charts-grid">
                <div class="chart-tabs">
                    <button class="chart-tab active" onclick="switchTab('genre', this)">Top Genres</button>
                    <button class="chart-tab" onclick="switchTab('mechanics', this)">Mécaniques</button>
                    <button class="chart-tab" onclick="switchTab('performance', this)">Performance</button>
                    <button class="chart-tab" onclick="switchTab('sector', this)">Secteurs</button>
                </div>
                <div class="chart-card active" id="tab-genre">
                    <div class="chart-title">Top Genres</div>
                    <canvas id="genreChart"></canvas>
                </div>
                <div class="chart-card" id="tab-mechanics">
                    <div class="chart-title">Mécaniques</div>
                    <canvas id="mechanicsChart"></canvas>
                </div>
                <div class="chart-card" id="tab-performance">
                    <div class="chart-title">Performance</div>
                    <canvas id="performanceChart"></canvas>
                </div>
                <div class="chart-card" id="tab-sector">
                    <div class="chart-title">Secteurs</div>
                    <canvas id="sectorChart"></canvas>
                </div>
            </div>
            
            <div class="table-card">
                <div class="chart-title">Top Îles (<span id="tableCount"></span>)</div>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th class="sortable" id="th-name" onclick="sortTable('name')">Nom</th>
                            <th class="sortable" id="th-genre" onclick="sortTable('genre')">Genre</th>
                            <th class="sortable" id="th-brand" onclick="sortTable('brand')">Partenariat</th>
                            <th class="sortable" id="th-players" onclick="sortTable('players')">Joueurs 24h</th>
                            <th class="sortable" id="th-peak_ccu" onclick="sortTable('peak_ccu')">Peak CCU 24h</th>
                            <th class="sortable" id="th-plays" onclick="sortTable('plays')">Sessions 24h</th>
                            <th class="sortable" id="th-retention_d1" onclick="sortTable('retention_d1')">Rét. D1</th>
                            <th class="sortable" id="th-retention_d7" onclick="sortTable('retention_d7')">Rét. D7</th>
                            <th class="sortable" id="th-avg_playtime" onclick="sortTable('avg_playtime')">Playtime moy.</th>
                            <th class="sortable" id="th-created_date" onclick="sortTable('created_date')">Sortie</th>
                            <th>Code</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
        </main>
    </div>
    
    <script>
        const allIslands = {islands_json};
        let filteredIslands = [...allIslands];
        let charts = {{}};
        let sortCol = 'unique_players';
        let sortDir = -1;

        function switchTab(name, btn) {{
            document.querySelectorAll('.chart-card').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.chart-tab').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + name).classList.add('active');
            btn.classList.add('active');
        }}

        function sortTable(col) {{
            if (sortCol === col) {{
                sortDir *= -1;
            }} else {{
                sortCol = col;
                sortDir = -1;
            }}
            updateSortIndicators();
            applyFilters();
        }}

        function updateSortIndicators() {{
            document.querySelectorAll('th.sortable').forEach(th => {{
                th.classList.remove('sort-asc', 'sort-desc');
            }});
            const th = document.getElementById('th-' + sortCol);
            if (th) th.classList.add(sortDir === 1 ? 'sort-asc' : 'sort-desc');
        }}

        function formatNumber(num) {{
            if (!num || num === 0) return 'N/A';
            if (num >= 1_000_000_000) return (num / 1_000_000_000).toFixed(1) + 'B';
            if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M';
            if (num >= 1_000) return num.toLocaleString('fr-FR');
            return num.toString();
        }}
        
        function toggleTheme() {{
            const html = document.documentElement;
            const themeSwitch = document.getElementById('themeSwitch');
            if (html.getAttribute('data-theme') === 'light') {{
                html.removeAttribute('data-theme');
                themeSwitch.classList.remove('active');
            }} else {{
                html.setAttribute('data-theme', 'light');
                themeSwitch.classList.add('active');
            }}
            updateCharts();
        }}
        
        function exportToExcel() {{
            const wb = XLSX.utils.book_new();
            const wsData = [['Nom', 'Genre', 'Joueurs', 'Code']];
            filteredIslands.forEach(i => wsData.push([i.name, i.genre.join(', '), i.players, i.code]));
            const ws = XLSX.utils.aoa_to_sheet(wsData);
            XLSX.utils.book_append_sheet(wb, ws, 'Islands');
            XLSX.writeFile(wb, 'fortnite_islands.xlsx');
        }}
        
        function populateFilters() {{
            const genres = new Set();
            const mechanics = new Set();
            const sectors = new Set();
            allIslands.forEach(i => {{
                i.genre.forEach(g => genres.add(g));
                i.mechanics.forEach(m => mechanics.add(m));
                sectors.add(i.sector);
            }});
            ['genre', 'mechanic', 'sector'].forEach(type => {{
                const select = document.getElementById(type + 'Filter');
                const items = type === 'genre' ? genres : type === 'mechanic' ? mechanics : sectors;
                [...items].sort().forEach(item => {{
                    const opt = document.createElement('option');
                    opt.value = item;
                    opt.textContent = item;
                    select.appendChild(opt);
                }});
            }});
        }}
        
        function applyFilters() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const genre = document.getElementById('genreFilter').value;
            const mechanic = document.getElementById('mechanicFilter').value;
            const sector = document.getElementById('sectorFilter').value;
            const sort = document.getElementById('sortBy').value;
            
            filteredIslands = allIslands.filter(i => {{
                return i.name.toLowerCase().includes(search) &&
                       (genre === 'all' || i.genre.includes(genre)) &&
                       (mechanic === 'all' || i.mechanics.includes(mechanic)) &&
                       (sector === 'all' || i.sector === sector);
            }});
            
            filteredIslands.sort((a, b) => {{
                if (sortCol === 'name') return sortDir * a.name.localeCompare(b.name);
                if (sortCol === 'genre') return sortDir * (a.genre[0] || '').localeCompare(b.genre[0] || '');
                if (sortCol === 'brand') return sortDir * (a.brand || '').localeCompare(b.brand || '');
                if (sortCol === 'avg_playtime') {{
                    const va = parseFloat(a.avg_playtime) || 0;
                    const vb = parseFloat(b.avg_playtime) || 0;
                    return sortDir * (va - vb);
                }}
                if (sortCol === 'created_date') {{
                    return sortDir * (new Date(a.created_date) - new Date(b.created_date));
                }}
                return sortDir * ((a[sortCol] || 0) - (b[sortCol] || 0));
            }});
            
            updateDashboard();
        }}
        
        function updateDashboard() {{
            updateInsights();
            updateKPIs();
            updateCharts();
            updateTable();
        }}
        
        function updateInsights() {{
            const total = filteredIslands.reduce((s, i) => s + i.players, 0);
            const avg = filteredIslands.length > 0 ? total / filteredIslands.length : 0;
            const genreCounts = {{}};
            filteredIslands.forEach(i => i.genre.forEach(g => genreCounts[g] = (genreCounts[g] || 0) + 1));
            const topGenre = Object.keys(genreCounts).sort((a,b) => genreCounts[b] - genreCounts[a])[0];
            
            document.getElementById('insightsSection').innerHTML = `
                <div class="insights-title">💡 Insights</div>
                <div class="insight-item">Genre dominant : ${{topGenre}} (${{genreCounts[topGenre]}} îles)</div>
                <div class="insight-item">Engagement moyen : ${{formatNumber(avg)}} joueurs/île</div>
            `;
        }}
        
        function updateKPIs() {{
            const n = filteredIslands.length;
            const totalUnique = filteredIslands.reduce((s, i) => s + i.players, 0);
            const totalSessions = filteredIslands.reduce((s, i) => s + i.plays, 0);
            const avgD1 = n > 0 ? filteredIslands.filter(i => i.retention_d1 > 0).reduce((s, i) => s + i.retention_d1, 0) / (filteredIslands.filter(i => i.retention_d1 > 0).length || 1) : 0;
            const avgPlaytime = filteredIslands.filter(i => i.avg_playtime && i.avg_playtime !== 'N/A').map(i => parseFloat(i.avg_playtime)).filter(v => !isNaN(v));
            const avgPlaytimeVal = avgPlaytime.length > 0 ? (avgPlaytime.reduce((a,b) => a+b, 0) / avgPlaytime.length).toFixed(1) : 'N/A';

            document.getElementById('kpiGrid').innerHTML = `
                <div class="kpi-card">
                    <div class="kpi-label">Total Îles</div>
                    <div class="kpi-value">${{n}}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Joueurs 24h (total)</div>
                    <div class="kpi-value">${{formatNumber(totalUnique)}}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Sessions 24h</div>
                    <div class="kpi-value">${{formatNumber(totalSessions)}}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Rétention D1 moy.</div>
                    <div class="kpi-value">${{avgD1.toFixed(1)}}%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Playtime moy.</div>
                    <div class="kpi-value">${{avgPlaytimeVal}} min</div>
                </div>
            `;
        }}
        
        function updateCharts() {{
            Object.values(charts).forEach(c => c.destroy());
            
            const genreCounts = {{}};
            filteredIslands.forEach(i => i.genre.forEach(g => genreCounts[g] = (genreCounts[g] || 0) + 1));
            
            charts.genre = new Chart(document.getElementById('genreChart'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(genreCounts).sort((a,b) => genreCounts[b] - genreCounts[a]).slice(0,10),
                    datasets: [{{label: 'Îles', data: Object.keys(genreCounts).sort((a,b) => genreCounts[b] - genreCounts[a]).slice(0,10).map(k => genreCounts[k]), backgroundColor: '#3b82f6'}}]
                }},
                options: {{responsive: true, aspectRatio: 4}}
            }});

            const mechCounts = {{}};
            filteredIslands.forEach(i => i.mechanics.forEach(m => mechCounts[m] = (mechCounts[m] || 0) + 1));
            charts.mechanics = new Chart(document.getElementById('mechanicsChart'), {{
                type: 'doughnut',
                data: {{labels: Object.keys(mechCounts), datasets: [{{data: Object.values(mechCounts), backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b']}}]}},
                options: {{responsive: true, aspectRatio: 2}}
            }});

            const genrePlayers = {{}};
            const genreCount = {{}};
            filteredIslands.forEach(i => i.genre.forEach(g => {{
                genrePlayers[g] = (genrePlayers[g] || 0) + i.players;
                genreCount[g] = (genreCount[g] || 0) + 1;
            }}));
            const avgByGenre = {{}};
            Object.keys(genrePlayers).forEach(g => avgByGenre[g] = genrePlayers[g] / genreCount[g]);
            charts.performance = new Chart(document.getElementById('performanceChart'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(avgByGenre).sort((a,b) => avgByGenre[b] - avgByGenre[a]).slice(0,10),
                    datasets: [{{label: 'Joueurs moyens', data: Object.keys(avgByGenre).sort((a,b) => avgByGenre[b] - avgByGenre[a]).slice(0,10).map(k => avgByGenre[k]), backgroundColor: '#8b5cf6'}}]
                }},
                options: {{responsive: true, aspectRatio: 4}}
            }});

            const sectorCounts = {{}};
            filteredIslands.forEach(i => sectorCounts[i.sector] = (sectorCounts[i.sector] || 0) + 1);
            charts.sector = new Chart(document.getElementById('sectorChart'), {{
                type: 'pie',
                data: {{labels: Object.keys(sectorCounts), datasets: [{{data: Object.values(sectorCounts), backgroundColor: ['#10b981', '#3b82f6', '#f59e0b']}}]}},
                options: {{responsive: true, aspectRatio: 2}}
            }});
        }}
        
        function updateTable() {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            document.getElementById('tableCount').textContent = filteredIslands.length;
            
            filteredIslands.forEach((island, i) => {{
                const row = tbody.insertRow();
                const isTop3 = i < 3;
                row.innerHTML = `
                    <td><span class="rank ${{isTop3 ? 'top' : ''}}">${{i + 1}}</span></td>
                    <td>${{island.name}}</td>
                    <td>${{island.genre.map(g => `<span class="badge">${{g}}</span>`).join('')}}</td>
                    <td>${{island.brand ? `<span class="brand-badge">${{island.brand}}</span>` : '—'}}</td>
                    <td>${{island.players_display}}</td>
                    <td>${{island.peak_ccu_display}}</td>
                    <td>${{island.plays_display}}</td>
                    <td>${{island.retention_d1_display}}</td>
                    <td>${{island.retention_d7_display}}</td>
                    <td>${{island.avg_playtime !== 'N/A' ? island.avg_playtime : '—'}}</td>
                    <td>${{island.created_date !== 'N/A' ? island.created_date : '—'}}</td>
                    <td><span class="code">${{island.code}}</span></td>
                `;
            }});
        }}
        
        document.getElementById('lastUpdated').textContent = new Date().toLocaleString('fr-FR');
        populateFilters();
        updateSortIndicators();
        applyFilters();
    </script>
</body>
</html>'''
    
    # Sauvegarder
    output_file = 'analytics_dashboard.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"{'='*70}")
    print(f"✅ DASHBOARD GÉNÉRÉ")
    print(f"💾 Fichier: {output_file}")
    print(f"{'='*70}\n")

    generate_recommendations_page(islands_json)

def generate_recommendations_page(islands_json):
    """Génère la page recommandations.html"""

    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recommandations — Fortnite Creative Analytics</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --bg-primary: #0d0d17;
            --bg-secondary: #13131f;
            --bg-card: #1c1c2e;
            --accent-purple: #7b2fbe;
            --accent-purple-light: #9b47e0;
            --accent-cyan: #00c8ff;
            --accent-green: #00c896;
            --text-primary: #ffffff;
            --text-secondary: #8b95a5;
            --border-color: #2a2a3e;
            --glow: 0 0 20px rgba(123, 47, 190, 0.3);
        }}
        body {{
            font-family: 'Inter', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: 280px 1fr;
            min-height: 100vh;
        }}
        .sidebar {{
            background: var(--bg-secondary);
            padding: 30px 20px;
            border-right: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }}
        .logo {{
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 8px;
            background: linear-gradient(90deg, var(--accent-purple-light), var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .nav-links {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-bottom: 36px;
        }}
        .nav-link {{
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 14px;
            color: var(--text-secondary);
            text-decoration: none;
            transition: all 0.2s;
        }}
        .nav-link:hover {{ background: var(--bg-card); color: var(--text-primary); }}
        .nav-link.active {{ background: var(--bg-card); color: var(--accent-cyan); font-weight: 600; }}
        .filter-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            margin-bottom: 10px;
            font-weight: 600;
        }}
        .filter-section {{ margin-bottom: 24px; }}
        .filter-select {{
            width: 100%;
            padding: 12px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 14px;
            cursor: pointer;
        }}
        .generate-btn {{
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-purple-light));
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            margin-top: 8px;
            transition: opacity 0.2s;
            box-shadow: var(--glow);
        }}
        .generate-btn:hover {{ opacity: 0.85; }}
        .main-content {{
            padding: 30px 40px;
            overflow-y: auto;
            max-height: 100vh;
        }}
        .header {{ margin-bottom: 30px; }}
        .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
        .header p {{ color: var(--text-secondary); font-size: 14px; }}
        .placeholder {{
            text-align: center;
            padding: 80px 40px;
            color: var(--text-secondary);
        }}
        .placeholder-icon {{ font-size: 60px; margin-bottom: 20px; }}
        .placeholder h2 {{ font-size: 20px; margin-bottom: 10px; color: var(--text-primary); }}
        .context-bar {{
            background: linear-gradient(135deg, var(--accent-purple), #3b1a6e);
            border: 1px solid rgba(123, 47, 190, 0.4);
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            box-shadow: var(--glow);
        }}
        .context-bar .ctx-title {{ font-size: 16px; font-weight: 700; }}
        .context-bar .ctx-sub {{ font-size: 13px; opacity: 0.85; margin-top: 4px; }}
        .context-bar .ctx-count {{
            font-size: 36px;
            font-weight: 700;
            text-align: right;
        }}
        .context-bar .ctx-count-label {{ font-size: 12px; opacity: 0.8; }}
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 16px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .combos-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
            margin-bottom: 36px;
        }}
        .combo-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            position: relative;
            transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
            overflow: hidden;
        }}
        .combo-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan));
        }}
        .combo-card:hover {{
            transform: translateY(-3px);
            border-color: var(--accent-purple);
            box-shadow: 0 0 24px rgba(123,47,190,0.4), 0 0 60px rgba(123,47,190,0.15);
        }}
        .combo-rank {{
            position: absolute;
            top: 16px;
            right: 16px;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 14px;
        }}
        .combo-rank.gold {{ background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #000; }}
        .combo-rank.silver {{ background: linear-gradient(135deg, #94a3b8, #64748b); color: #fff; }}
        .combo-rank.bronze {{ background: linear-gradient(135deg, #cd7c3a, #a05a2c); color: #fff; }}
        .combo-rank.default {{ background: var(--bg-secondary); color: var(--text-secondary); }}
        .combo-badges {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }}
        .badge-genre {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(0, 200, 255, 0.12);
            color: var(--accent-cyan);
            border: 1px solid rgba(0, 200, 255, 0.25);
        }}
        .badge-mechanic {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(123, 47, 190, 0.18);
            color: var(--accent-purple-light);
            border: 1px solid rgba(123, 47, 190, 0.3);
        }}
        .combo-stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 12px;
        }}
        .combo-stat-label {{ font-size: 11px; color: var(--text-secondary); }}
        .combo-stat-value {{ font-size: 18px; font-weight: 700; }}
        .combo-examples {{
            font-size: 12px;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
            padding-top: 10px;
        }}
        .combo-examples span {{ color: var(--text-primary); }}
        .no-results {{
            text-align: center;
            padding: 60px;
            color: var(--text-secondary);
            background: var(--bg-card);
            border-radius: 12px;
        }}
    </style>
</head>
<body>
<div class="dashboard">
    <aside class="sidebar">
        <div class="logo">🎮 Fortnite Analytics</div>
        <nav class="nav-links">
            <a href="analytics_dashboard.html" class="nav-link">📊 Dashboard</a>
            <a href="recommandations.html" class="nav-link active">💡 Recommandations</a>
        </nav>

        <div class="filter-section">
            <div class="filter-label">Marque / IP</div>
            <select id="brandSelect" class="filter-select">
                <option value="">— Toutes les marques —</option>
            </select>
        </div>

        <div class="filter-section">
            <div class="filter-label">Secteur d\'activité</div>
            <select id="sectorSelect" class="filter-select">
                <option value="">— Tous les secteurs —</option>
            </select>
        </div>

        <button class="generate-btn" onclick="generate()">🔍 Analyser</button>
    </aside>

    <main class="main-content">
        <div class="header">
            <h1>Recommandations créatives</h1>
            <p>Choisissez une marque et/ou un secteur pour obtenir les meilleures combinaisons genre + mécanique.</p>
        </div>

        <div id="results">
            <div class="placeholder">
                <div class="placeholder-icon">🗺️</div>
                <h2>Prêt à analyser</h2>
                <p>Sélectionnez une marque et/ou un secteur dans le panneau gauche, puis cliquez sur Analyser.</p>
            </div>
        </div>
    </main>
</div>

<script>
    const allIslands = {islands_json};

    // Populate selectors
    const brands = [...new Set(allIslands.map(i => i.brand).filter(Boolean))].sort();
    const sectors = [...new Set(allIslands.map(i => i.sector).filter(Boolean))].sort();

    const brandSel = document.getElementById('brandSelect');
    const sectorSel = document.getElementById('sectorSelect');

    brands.forEach(b => {{ const o = document.createElement('option'); o.value = b; o.textContent = b; brandSel.appendChild(o); }});
    sectors.forEach(s => {{ const o = document.createElement('option'); o.value = s; o.textContent = s; sectorSel.appendChild(o); }});

    function formatPlayers(n) {{
        if (!n || n === 0) return 'N/A';
        if (n >= 1_000_000_000) return (n / 1_000_000_000).toFixed(1) + 'B';
        if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
        if (n >= 1_000) return (n / 1_000).toFixed(0) + 'K';
        return n.toString();
    }}

    function rankClass(i) {{
        if (i === 0) return 'gold';
        if (i === 1) return 'silver';
        if (i === 2) return 'bronze';
        return 'default';
    }}

    function generate() {{
        const brand  = brandSel.value;
        const sector = sectorSel.value;

        if (!brand && !sector) {{
            document.getElementById('results').innerHTML = `
                <div class="no-results">⚠️ Sélectionnez au moins une marque ou un secteur.</div>`;
            return;
        }}

        // Filter
        const filtered = allIslands.filter(i =>
            (!brand  || i.brand  === brand)  &&
            (!sector || i.sector === sector)
        );

        if (filtered.length === 0) {{
            document.getElementById('results').innerHTML = `
                <div class="no-results">Aucune île trouvée pour cette sélection.</div>`;
            return;
        }}

        // Build combo scores
        const combos = {{}};
        filtered.forEach(island => {{
            island.genre.forEach(g => {{
                island.mechanics.forEach(m => {{
                    const key = g + '|||' + m;
                    if (!combos[key]) combos[key] = {{ genre: g, mechanic: m, count: 0, totalPlayers: 0, islands: [] }};
                    combos[key].count++;
                    combos[key].totalPlayers += (island.players || 0);
                    if (combos[key].islands.length < 3) combos[key].islands.push(island.name);
                }});
            }});
        }});

        // Score = avgPlayers * sqrt(count) — équilibre perf + fréquence
        const ranked = Object.values(combos)
            .map(c => ({{ ...c, avgPlayers: c.count > 0 ? c.totalPlayers / c.count : 0,
                          score: (c.totalPlayers / (c.count || 1)) * Math.sqrt(c.count) }}))
            .sort((a, b) => b.score - a.score)
            .slice(0, 9);

        const ctxLabel = [brand, sector].filter(Boolean).join(' · ');

        let html = `
            <div class="context-bar">
                <div>
                    <div class="ctx-title">Analyse : ${{ctxLabel}}</div>
                    <div class="ctx-sub">Top combinaisons genre + mécanique classées par score de performance</div>
                </div>
                <div style="text-align:right">
                    <div class="ctx-count">${{filtered.length}}</div>
                    <div class="ctx-count-label">îles analysées</div>
                </div>
            </div>
            <div class="section-title">Top combinaisons recommandées</div>
            <div class="combos-grid">`;

        ranked.forEach((combo, i) => {{
            html += `
                <div class="combo-card">
                    <span class="combo-rank ${{rankClass(i)}}">${{i + 1}}</span>
                    <div class="combo-badges">
                        <span class="badge-genre">${{combo.genre}}</span>
                        <span class="badge-mechanic">${{combo.mechanic}}</span>
                    </div>
                    <div class="combo-stats">
                        <div>
                            <div class="combo-stat-label">Joueurs moy.</div>
                            <div class="combo-stat-value">${{formatPlayers(combo.avgPlayers)}}</div>
                        </div>
                        <div>
                            <div class="combo-stat-label">Îles</div>
                            <div class="combo-stat-value">${{combo.count}}</div>
                        </div>
                    </div>
                    <div class="combo-examples">
                        Exemples : <span>${{combo.islands.map(n => n.length > 30 ? n.slice(0,28)+'…' : n).join(', ')}}</span>
                    </div>
                </div>`;
        }});

        html += `</div>`;
        document.getElementById('results').innerHTML = html;
    }}
</script>
</body>
</html>'''

    with open('recommandations.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ recommandations.html généré")


if __name__ == "__main__":
    update_dashboard()