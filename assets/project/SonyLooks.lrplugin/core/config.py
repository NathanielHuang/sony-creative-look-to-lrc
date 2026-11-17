from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def load_adapter(path=None):return read_json(path or ROOT/'adapter.json')
def load_recipes():return read_json(ROOT/'recipes.json')
