"""
Scheduler : Lance le pipeline complet tous les jours à l'heure configurée.
Les snapshots quotidiens permettront l'analyse de l'évolution temporelle.

Usage:
  python scheduler.py             # Lance à 06:00 chaque jour (défaut)
  python scheduler.py --now       # Lance immédiatement puis reprend le planning
  python scheduler.py --hour 08   # Lance à 08:00 chaque jour

Laisser tourner en arrière-plan (ex: dans un terminal dédié).
"""

import os
import shutil
import subprocess
import sys
import argparse
from datetime import datetime
import schedule
import time

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

def _python():
    if shutil.which('py'):
        return ['py', '-3.9']
    return [sys.executable]


def run_pipeline():
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{ts}] Lancement du pipeline...")

    result = subprocess.run(
        _python() + ['pipeline.py'],
        cwd=SCRIPTS_DIR,
        env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
    )

    ts_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if result.returncode == 0:
        print(f"[{ts_end}] Pipeline termine avec succes")
    else:
        print(f"[{ts_end}] Pipeline echoue (code {result.returncode})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--now',  action='store_true', help='Lance le pipeline immediatement en plus du planning')
    parser.add_argument('--hour', type=str, default='06', help='Heure de lancement quotidien (ex: 06, 08, 22)')
    args = parser.parse_args()

    run_time = f"{args.hour.zfill(2)}:00"

    schedule.every().day.at(run_time).do(run_pipeline)

    print(f"\n{'='*50}")
    print(f"  SCHEDULER FORTNITE ANALYTICS")
    print(f"  Pipeline lance tous les jours a {run_time}")
    print(f"  Prochaine execution: {schedule.next_run()}")
    print(f"  Ctrl+C pour arreter")
    print(f"{'='*50}\n")

    if args.now:
        run_pipeline()

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
