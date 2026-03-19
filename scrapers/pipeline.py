"""
Pipeline complet : Scrape → Clean → Categorize → Dashboard

Usage:
  python pipeline.py           # scraping + tout
  python pipeline.py --no-scrape  # clean + categorize + dashboard (données déjà scrapées)
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime

SCRIPTS_DIR   = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(SCRIPTS_DIR, '..', 'dashboard')

# Utiliser py -3.9 si disponible (toutes les dépendances y sont installées),
# sinon fallback sur sys.executable
def _python():
    if shutil.which('py'):
        return ['py', '-3.9']
    return [sys.executable]


def run(label, script, cwd):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  {script}")
    print(f"{'='*60}")

    result = subprocess.run(
        _python() + [script],
        cwd=cwd,
        env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
    )

    if result.returncode != 0:
        print(f"\nECHEC: {script} (code {result.returncode})")
        sys.exit(result.returncode)


def main():
    no_scrape = '--no-scrape' in sys.argv

    start = datetime.now()
    print(f"\n{'='*60}")
    print(f"  PIPELINE FORTNITE ANALYTICS")
    print(f"  Debut: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    if no_scrape:
        print(f"  Mode: --no-scrape (skip scraper_v2)")
    print(f"{'='*60}")

    steps = []

    if not no_scrape:
        steps.append(("1/4  Scraping (scraper_v2)", 'scraper_v2.py', SCRIPTS_DIR))

    steps += [
        ("2/4  Nettoyage (clean_data_enriched)", 'clean_data_enriched.py', SCRIPTS_DIR),
        ("3/4  Categorisation (categorize_islands)", 'categorize_islands.py', SCRIPTS_DIR),
        ("4/4  Dashboard (update_dashboard)", 'update_dashboard.py', DASHBOARD_DIR),
    ]

    for label, script, cwd in steps:
        run(label, script, cwd)

    elapsed = (datetime.now() - start).seconds // 60
    print(f"\n{'='*60}")
    print(f"  PIPELINE TERMINE en ~{elapsed} min")
    print(f"  Dashboard: dashboard/analytics_dashboard.html")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
