import csv
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_script():
    spec = importlib.util.spec_from_file_location('insider_threat_detection', os.path.join(ROOT, 'insider_threat_detection.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_standalone_matches_published_risk_scores(tmp_path, capsys):
    script = _load_script()
    out = tmp_path / 'results.csv'
    results = script.main(['--out', str(out)])
    assert 'Risk distribution' in capsys.readouterr().out

    with open(os.path.join(ROOT, 'datasets', 'risk_scores.csv'), newline='') as f:
        published = {r['user_id']: (float(r['normalized_risk_score']), r['risk_category']) for r in csv.DictReader(f)}
    assert {r['user_id']: (r['risk_score'], r['risk_category']) for r in results} == published
    assert out.exists()
