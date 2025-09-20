from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SHOTS_DIR = BASE_DIR / "shots"       # where screenshots will be saved
GIFTS_REF = BASE_DIR / "gifts_ref"   # folder with reference gift images

SHOTS_DIR.mkdir(parents=True, exist_ok=True)
GIFTS_REF.mkdir(parents=True, exist_ok=True)

CFG = {
    "BASE_DIR": BASE_DIR,
    "SHOTS_DIR": SHOTS_DIR,
    "GIFTS_REF": GIFTS_REF,
}