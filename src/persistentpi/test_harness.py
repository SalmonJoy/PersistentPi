"""Fixed reviewed-fixture test entry point, launched in an isolated interpreter."""
from pathlib import Path
import sys
import unittest


def main():
    workspace, suite = map(Path, sys.argv[1:3])
    policy = sys.argv[3] if len(sys.argv) > 3 else 'reviewed_python'
    if policy == 'bounded-python-1':
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from bounded_python import module, PolicyError
        try:
            for path in sorted((workspace / 'src').glob('*.py')):
                if path.stem in sys.modules or not path.stem.isidentifier() or path.stem.startswith('_'):
                    raise PolicyError('Reserved module name')
                sys.modules[path.stem] = module(path.stem, path.read_text(encoding='utf-8'))
        except (ValueError, SyntaxError) as exc:
            print('Candidate rejected by bounded Python policy: ' + str(exc))
            return 1
    elif policy == 'reviewed_python':
        sys.path.insert(0, str(workspace / 'src'))
    else:
        print('Unsupported execution policy')
        return 2
    tests = unittest.defaultTestLoader.discover(str(suite), pattern='test_*.py')
    if tests.countTestCases() == 0:
        print('No tests discovered', file=sys.stderr)
        return 2
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.skipped or result.expectedFailures:
        print('Incomplete test evidence: skipped/expected-failure tests', file=sys.stderr)
        return 2
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
