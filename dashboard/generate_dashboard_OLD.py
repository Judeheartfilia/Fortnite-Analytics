import json

def generate_dashboard():
    """Génère le dashboard HTML avec les données intégrées"""
    
    print(f"\n{'='*70}")
    print(f"🎨 GÉNÉRATION DU DASHBOARD ANALYTIQUE")
    print(f"{'='*70}\n")
    
    # Charger les données catégorisées
    print("📂 Chargement des données...")
    with open('../data/processed/islands_categorized.json', 'r', encoding='utf-8') as f:
        islands = json.load(f)
    
    print(f"✅ {len(islands)} îles chargées\n")
    
    # Convertir en format JavaScript
    islands_js = []
    for island in islands:
        # Extraire le nombre de joueurs
        players_str = island.get('players', '0')
        if isinstance(players_str, str):
            if 'M' in players_str:
                players = float(players_str.replace('M', '')) * 1_000_000
            elif 'K' in players_str:
                players = float(players_str.replace('K', '')) * 1_000
            else:
                players = 0
        else:
            players = 0
        
        # Extraire favoris
        # Note: Le champ peut être dans 'stats' ou directement
        # On va chercher dans le texte brut des noms
        name_parts = island['name'].split('\n')
        favorites = 0
        for part in name_parts:
            if 'K' in part:
                try:
                    fav_str = part.replace('K', '').strip()
                    favorites = float(fav_str) * 1000
                    break
                except:
                    pass
        
        islands_js.append({
            'name': island['name'].split('\n')[-1] if '\n' in island['name'] else island['name'],
            'code': island['code'],
            'players': int(players),
            'favorites': int(favorites),
            'genre': island.get('genre', ['Autre']),
            'mechanics': island.get('mechanics', ['Autre']),
            'sector': island.get('sector', 'Gaming Pure'),
            'stats': island.get('stats', [])
        })
    
    # Générer le HTML complet
    html_content = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fortnite Creative Analytics - Dashboard Stratégique</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .filters {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}
        
        .filter-group {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .filter-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .filter-item label {{
            font-size: 0.9em;
            margin-bottom: 5px;
            opacity: 0.8;
        }}
        
        .filter-item select {{
            padding: 10px;
            border-radius: 8px;
            border: none;
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
            font-size: 1em;
            cursor: pointer;
        }}
        
        .filter-item select option {{
            background: #667eea;
            color: #fff;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .stat-label {{
            font-size: 1em;
            opacity: 0.8;
        }}
        
        .charts-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .chart-container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}
        
        .chart-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .table-container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        th {{
            background: rgba(255, 255, 255, 0.1);
            font-weight: bold;
            cursor: pointer;
        }}
        
        th:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}
        
        tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.2);
            font-size: 0.85em;
            margin-right: 5px;
            margin-bottom: 3px;
        }}
        
        @media (max-width: 768px) {{
            .charts-section {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎮 Fortnite Creative Analytics</h1>
            <p class="subtitle">Dashboard Stratégique d'Analyse des Performances</p>
        </header>
        
        <div class="filters">
            <h3 style="margin-bottom: 15px;">🔍 Filtres Dynamiques</h3>
            <div class="filter-group">
                <div class="filter-item">
                    <label>Genre</label>
                    <select id="genreFilter" onchange="applyFilters()">
                        <option value="all">Tous les genres</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label>Mécanique</label>
                    <select id="mechanicFilter" onchange="applyFilters()">
                        <option value="all">Toutes les mécaniques</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label>Secteur</label>
                    <select id="sectorFilter" onchange="applyFilters()">
                        <option value="all">Tous les secteurs</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label>Tri par</label>
                    <select id="sortBy" onchange="applyFilters()">
                        <option value="players">Joueurs (décroissant)</option>
                        <option value="favorites">Favoris (décroissant)</option>
                        <option value="name">Nom (A-Z)</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="stats-grid" id="statsGrid"></div>
        
        <div class="charts-section">
            <div class="chart-container">
                <h3 class="chart-title">📊 Top Genres par Nombre d'Îles</h3>
                <canvas id="genreChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3 class="chart-title">⚙️ Top Mécaniques de Gameplay</h3>
                <canvas id="mechanicsChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3 class="chart-title">🏢 Répartition par Secteur</h3>
                <canvas id="sectorChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3 class="chart-title">💎 Performance par Genre</h3>
                <canvas id="performanceChart"></canvas>
            </div>
        </div>
        
        <div class="table-container">
            <h3 class="chart-title">📋 Liste Complète des Îles Filtrées</h3>
            <table id="islandsTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">#</th>
                        <th onclick="sortTable(1)">Nom</th>
                        <th onclick="sortTable(2)">Genre</th>
                        <th onclick="sortTable(3)">Mécaniques</th>
                        <th onclick="sortTable(4)">Secteur</th>
                        <th onclick="sortTable(5)">Joueurs 24h</th>
                        <th onclick="sortTable(6)">Favoris</th>
                        <th onclick="sortTable(7)">Code</th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Données des îles (générées automatiquement)
        const allIslands = {json.dumps(islands_js, ensure_ascii=False)};
        
        let filteredIslands = [...allIslands];
        let charts = {{}};
        
        function formatNumber(num) {{
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toString();
        }}
        
        function populateFilters() {{
            const genres = new Set();
            const mechanics = new Set();
            const sectors = new Set();
            
            allIslands.forEach(island => {{
                island.genre.forEach(g => genres.add(g));
                island.mechanics.forEach(m => mechanics.add(m));
                sectors.add(island.sector);
            }});
            
            const genreFilter = document.getElementById('genreFilter');
            [...genres].sort().forEach(g => {{
                const opt = document.createElement('option');
                opt.value = g;
                opt.textContent = g;
                genreFilter.appendChild(opt);
            }});
            
            const mechanicFilter = document.getElementById('mechanicFilter');
            [...mechanics].sort().forEach(m => {{
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                mechanicFilter.appendChild(opt);
            }});
            
            const sectorFilter = document.getElementById('sectorFilter');
            [...sectors].sort().forEach(s => {{
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                sectorFilter.appendChild(opt);
            }});
        }}
        
        function applyFilters() {{
            const genreFilter = document.getElementById('genreFilter').value;
            const mechanicFilter = document.getElementById('mechanicFilter').value;
            const sectorFilter = document.getElementById('sectorFilter').value;
            const sortBy = document.getElementById('sortBy').value;
            
            filteredIslands = allIslands.filter(island => {{
                const matchGenre = genreFilter === 'all' || island.genre.includes(genreFilter);
                const matchMechanic = mechanicFilter === 'all' || island.mechanics.includes(mechanicFilter);
                const matchSector = sectorFilter === 'all' || island.sector === sectorFilter;
                
                return matchGenre && matchMechanic && matchSector;
            }});
            
            // Tri
            if (sortBy === 'players') {{
                filteredIslands.sort((a, b) => b.players - a.players);
            }} else if (sortBy === 'favorites') {{
                filteredIslands.sort((a, b) => b.favorites - a.favorites);
            }} else if (sortBy === 'name') {{
                filteredIslands.sort((a, b) => a.name.localeCompare(b.name));
            }}
            
            updateDashboard();
        }}
        
        function updateDashboard() {{
            updateStats();
            updateCharts();
            updateTable();
        }}
        
        function updateStats() {{
            const totalPlayers = filteredIslands.reduce((sum, i) => sum + i.players, 0);
            const avgPlayers = filteredIslands.length > 0 ? totalPlayers / filteredIslands.length : 0;
            const totalFavorites = filteredIslands.reduce((sum, i) => sum + i.favorites, 0);
            
            // Top genre
            const genreCounts = {{}};
            filteredIslands.forEach(island => {{
                island.genre.forEach(g => {{
                    genreCounts[g] = (genreCounts[g] || 0) + 1;
                }});
            }});
            const topGenre = Object.keys(genreCounts).sort((a, b) => genreCounts[b] - genreCounts[a])[0] || 'N/A';
            
            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Îles Affichées</div>
                    <div class="stat-value">${{filteredIslands.length}}</div>
                    <div class="stat-label">sur ${{allIslands.length}} total</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Joueurs 24h</div>
                    <div class="stat-value">${{formatNumber(totalPlayers)}}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Moyenne Joueurs</div>
                    <div class="stat-value">${{formatNumber(avgPlayers)}}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Genre Dominant</div>
                    <div class="stat-value" style="font-size:1.8em;">${{topGenre}}</div>
                </div>
            `;
        }}
        
        function updateCharts() {{
            // Détruire les anciens graphiques
            Object.values(charts).forEach(chart => chart.destroy());
            charts = {{}};
            
            // Genre Chart
            const genreCounts = {{}};
            filteredIslands.forEach(island => {{
                island.genre.forEach(g => {{
                    genreCounts[g] = (genreCounts[g] || 0) + 1;
                }});
            }});
            
            charts.genre = new Chart(document.getElementById('genreChart'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(genreCounts).sort((a,b) => genreCounts[b] - genreCounts[a]),
                    datasets: [{{
                        label: 'Nombre d\\'îles',
                        data: Object.keys(genreCounts).sort((a,b) => genreCounts[b] - genreCounts[a]).map(k => genreCounts[k]),
                        backgroundColor: 'rgba(74, 222, 128, 0.8)',
                        borderColor: 'rgba(74, 222, 128, 1)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {{
                        y: {{beginAtZero: true, ticks: {{color: '#fff'}}, grid: {{color: 'rgba(255,255,255,0.1)'}}}},
                        x: {{ticks: {{color: '#fff'}}, grid: {{color: 'rgba(255,255,255,0.1)'}}}}
                    }},
                    plugins: {{legend: {{labels: {{color: '#fff'}}}}}}
                }}
            }});
            
            // Mechanics Chart
            const mechanicCounts = {{}};
            filteredIslands.forEach(island => {{
                island.mechanics.forEach(m => {{
                    mechanicCounts[m] = (mechanicCounts[m] || 0) + 1;
                }});
            }});
            
            charts.mechanics = new Chart(document.getElementById('mechanicsChart'), {{
                type: 'doughnut',
                data: {{
                    labels: Object.keys(mechanicCounts),
                    datasets: [{{
                        data: Object.values(mechanicCounts),
                        backgroundColor: [
                            'rgba(239, 68, 68, 0.8)',
                            'rgba(59, 130, 246, 0.8)',
                            'rgba(168, 85, 247, 0.8)',
                            'rgba(34, 197, 94, 0.8)',
                            'rgba(251, 146, 60, 0.8)',
                            'rgba(236, 72, 153, 0.8)'
                        ],
                        borderColor: '#fff',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{position: 'bottom', labels: {{color: '#fff', padding: 15}}}}
                    }}
                }}
            }});
            
            // Sector Chart
            const sectorCounts = {{}};
            filteredIslands.forEach(island => {{
                sectorCounts[island.sector] = (sectorCounts[island.sector] || 0) + 1;
            }});
            
            charts.sector = new Chart(document.getElementById('sectorChart'), {{
                type: 'pie',
                data: {{
                    labels: Object.keys(sectorCounts),
                    datasets: [{{
                        data: Object.values(sectorCounts),
                        backgroundColor: [
                            'rgba(74, 222, 128, 0.8)',
                            'rgba(59, 130, 246, 0.8)',
                            'rgba(251, 146, 60, 0.8)'
                        ],
                        borderColor: '#fff',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{position: 'bottom', labels: {{color: '#fff'}}}}
                    }}
                }}
            }});
            
            // Performance Chart - Joueurs moyens par genre
            const genrePlayers = {{}};
            const genrePlayerCounts = {{}};
            
            filteredIslands.forEach(island => {{
                island.genre.forEach(g => {{
                    genrePlayers[g] = (genrePlayers[g] || 0) + island.players;
                    genrePlayerCounts[g] = (genrePlayerCounts[g] || 0) + 1;
                }});
            }});
            
            const avgByGenre = {{}};
            Object.keys(genrePlayers).forEach(g => {{
                avgByGenre[g] = genrePlayers[g] / genrePlayerCounts[g];
            }});
            
            charts.performance = new Chart(document.getElementById('performanceChart'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(avgByGenre).sort((a,b) => avgByGenre[b] - avgByGenre[a]),
                    datasets: [{{
                        label: 'Joueurs moyens par île',
                        data: Object.keys(avgByGenre).sort((a,b) => avgByGenre[b] - avgByGenre[a]).map(k => avgByGenre[k]),
                        backgroundColor: 'rgba(168, 85, 247, 0.8)',
                        borderColor: 'rgba(168, 85, 247, 1)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true, 
                            ticks: {{
                                color: '#fff',
                                callback: function(value) {{
                                    return formatNumber(value);
                                }}
                            }}, 
                            grid: {{color: 'rgba(255,255,255,0.1)'}}
                        }},
                        x: {{ticks: {{color: '#fff'}}, grid: {{color: 'rgba(255,255,255,0.1)'}}}}
                    }},
                    plugins: {{legend: {{labels: {{color: '#fff'}}}}}}
                }}
            }});
        }}
        
        function updateTable() {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            
            filteredIslands.forEach((island, index) => {{
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${{index + 1}}</td>
                    <td>${{island.name}}</td>
                    <td>${{island.genre.map(g => `<span class="badge">${{g}}</span>`).join('')}}</td>
                    <td>${{island.mechanics.slice(0,2).map(m => `<span class="badge">${{m}}</span>`).join('')}}</td>
                    <td>${{island.sector}}</td>
                    <td>${{formatNumber(island.players)}}</td>
                    <td>${{formatNumber(island.favorites)}}</td>
                    <td><code>${{island.code}}</code></td>
                `;
            }});
        }}
        
        // Initialisation
        populateFilters();
        updateDashboard();
    </script>
</body>
</html>'''
    
    # Sauvegarder le dashboard
    output_file = 'analytics_dashboard.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"{'='*70}")
    print(f"✅ DASHBOARD GÉNÉRÉ")
    print(f"💾 Fichier: {output_file}")
    print(f"🌐 Ouvre ce fichier dans ton navigateur !")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    generate_dashboard()