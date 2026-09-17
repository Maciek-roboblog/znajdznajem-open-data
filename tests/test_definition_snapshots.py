import importlib.util
import csv
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('publisher', Path(__file__).parents[1] / 'scripts' / 'publish.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)

CITY = {'slug': 'warszawa', 'name': 'Warszawa'}
DEFINITION = {'status': 'known', 'version': 'old-rules-v1', 'sha256': 'old-hash', 'content': {'active_offer': 'rules when the numbers were computed'}}


class DefinitionSnapshotsTest(unittest.TestCase):
    def test_weekly_files_keep_definition_in_actual_csv_and_json(self):
        report = {'overview': {'total_offers': 12}, 'definition': DEFINITION}
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            with patch.object(publisher, 'REPO', base), patch.object(publisher, 'get', side_effect=[report, {}]), patch.object(publisher, 'commit'), patch.object(publisher, 'prepend_changelog'):
                publisher.weekly(date(2026, 9, 18), [CITY], dry_run=True)
            with (base / 'data/latest/city-stats.csv').open() as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(json.loads(row['definition_json']), DEFINITION)
            self.assertEqual(row['definition_version'], DEFINITION['version'])
            self.assertEqual(row['definition_sha256'], DEFINITION['sha256'])
            raw = json.loads((base / 'data/latest/raw/warszawa.json').read_text())
            self.assertEqual(raw['report']['definition'], DEFINITION)

    def test_weekly_row_and_raw_keep_the_same_pinned_rules(self):
        report = {'overview': {'total_offers': 12}, 'definition': DEFINITION}
        with patch.object(publisher, 'get', side_effect=[report, {}]) as get:
            row, raw = publisher.city_row(date(2026, 9, 18), CITY)
        self.assertEqual(json.loads(row['definition_json']), DEFINITION)
        self.assertEqual(raw['report']['definition'], DEFINITION)
        self.assertEqual(get.call_count, 2)  # No fetch of today's definitions.

    def test_legacy_export_explicitly_remains_unknown(self):
        report = {'overview': {'total_offers': 12}}
        with patch.object(publisher, 'get', side_effect=[report, {}]):
            row, raw = publisher.city_row(date(2026, 9, 18), CITY)
        self.assertEqual(json.loads(row['definition_json'])['status'], 'unknown')
        self.assertIsNone(raw['report']['definition']['version'])
        self.assertNotIn('definition', report)  # Do not mutate the fetched snapshot.
        rendered = publisher.render_report('2025-01', CITY, report)
        self.assertIn('Wersja definicji: nieznana', rendered)
        self.assertNotIn('po deduplikacji', rendered)

    def test_monthly_json_preserves_definition_and_does_not_rewrite_old_files(self):
        original = {'overview': {'total_offers': 12}, 'definition': DEFINITION}
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            old = base / 'reports' / '2025-01'
            old.mkdir(parents=True)
            (old / 'warszawa.json').write_text('{"old":true}')
            def get(path, **kwargs):
                if path.endswith('/months'):
                    return {'months': ['2025-01', '2026-09']}
                return original
            with patch.object(publisher, 'REPO', base), patch.object(publisher, 'get', side_effect=get), patch.object(publisher, 'commit'), patch.object(publisher, 'prepend_changelog'):
                publisher.monthly([CITY], dry_run=True)
            self.assertEqual((old / 'warszawa.json').read_text(), '{"old":true}')
            exported = json.loads((base / 'reports' / '2026-09' / 'warszawa.json').read_text())
            self.assertEqual(exported['definition'], DEFINITION)
