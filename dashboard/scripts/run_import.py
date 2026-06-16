"""Thin wrapper around the importer CLI so it can be run as a script.

Usage examples:
  python dashboard/scripts/run_import.py                      # all authorities
  python dashboard/scripts/run_import.py --authority Cotswold --days 30
  python dashboard/scripts/run_import.py --force-backfill -v

Schedule this daily (e.g. Windows Task Scheduler) for an automatic refresh.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planning_dashboard.importer import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
