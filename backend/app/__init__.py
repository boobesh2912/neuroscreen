"""MediGuardian FastAPI application package."""

from pathlib import Path
import sys

# Make project root importable so legacy modules can be reused.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
