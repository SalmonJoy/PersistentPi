"""Run only distributed offline tests; no research inference or benchmark access."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
from persistentpi.artifacts import atomic_write
from persistentpi.contracts import canonical


def main():
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {'scope': 'public distributed offline subset', 'tests_run': result.testsRun,
               'passed': result.wasSuccessful(), 'skipped': len(result.skipped),
               'errors': len(result.errors), 'failures': len(result.failures),
               'research_inference': 0, 'benchmark_execution': 0,
               'excluded_tests_are_not_public_passes': True}
    atomic_write(ROOT / '.local/public-validation.json', canonical(receipt))
    print(json.dumps(receipt))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
