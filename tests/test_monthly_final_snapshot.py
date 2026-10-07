import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('publisher', Path(__file__).parents[1] / 'scripts' / 'publish.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)

CITIES = [{'slug': 'krakow', 'name': 'Kraków'}, {'slug': 'warszawa', 'name': 'Warszawa'}]


def api(generated_at):
    """Fake API: one archived month (2026-09) whose snapshots were generated at the given time per city."""
    def get(path, **params):
        if path == '/stats/report/months':
            return {'months': ['2026-09']}
        return {'overview': {'total_offers': 10}, 'generated_at': generated_at[params['city']]}
    return get


class MonthlyFinalSnapshotTest(unittest.TestCase):
    def run_monthly(self, generated_at):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            with patch.object(publisher, 'REPO', base), patch.object(publisher, 'get', side_effect=api(generated_at)), \
                    patch.object(publisher, 'commit') as commit, patch.object(publisher, 'prepend_changelog'):
                publisher.monthly(CITIES, dry_run=True)
            return sorted(p.name for p in (base / 'reports' / '2026-09').glob('*')), commit.call_count

    def test_a_snapshot_taken_before_the_month_ended_is_not_published(self):
        # 2026-09-21: the app already had a 2026-09 archive, generated on the 19th; it went out as the monthly report.
        files, commits = self.run_monthly({'krakow': '2026-09-19T23:36:56+02:00', 'warszawa': '2026-09-19T23:36:58+02:00'})
        self.assertEqual((files, commits), ([], 0))

    def test_one_unfinished_city_holds_back_the_whole_month(self):
        files, commits = self.run_monthly({'krakow': '2026-10-01T03:00:31+02:00', 'warszawa': '2026-09-19T23:36:58+02:00'})
        self.assertEqual((files, commits), ([], 0))

    def test_a_snapshot_without_a_generation_time_is_not_published(self):
        files, commits = self.run_monthly({'krakow': None, 'warszawa': None})
        self.assertEqual((files, commits), ([], 0))

    def test_a_snapshot_taken_after_the_month_ended_is_published(self):
        files, commits = self.run_monthly({'krakow': '2026-10-01T03:00:31+02:00', 'warszawa': '2026-10-01T03:00:33+02:00'})
        self.assertEqual(files, ['README.md', 'krakow.json', 'krakow.md', 'warszawa.json', 'warszawa.md'])
        self.assertEqual(commits, 1)


if __name__ == '__main__':
    unittest.main()
