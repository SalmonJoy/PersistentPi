"""Trusted JSON-case harness. Runs candidates only in the bounded interpreter."""
import json
from pathlib import Path
import sys
import traceback

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bounded_python import Interpreter


def main():
    source, cases_path, output = map(Path,sys.argv[1:4])
    cases = json.loads(cases_path.read_bytes())
    results = []
    try:
        interpreter = Interpreter(source.read_text(encoding='utf-8'))
    except (ValueError, SyntaxError) as exc:
        interpreter = None
        parse_error = exc
    for case in cases:
        record = {'id':case['id'],'outcome':'pass','type':None,'message':'','traceback':''}
        try:
            if interpreter is None:
                raise parse_error
            actual = interpreter.call('solve',case['args'])
            if type(actual) != type(case['expected']) or actual != case['expected']:
                raise AssertionError(f"expected {case['expected']!r}; actual {actual!r}")
        except Exception as exc:
            record.update(outcome='fail',type=type(exc).__name__,message=str(exc),
                          traceback=''.join(traceback.format_exception_only(type(exc),exc)))
        results.append(record)
    outcome = 'pass' if all(c['outcome']=='pass' for c in results) else 'fail'
    # Structured evidence is written to control-plane-owned storage, not by candidate code.
    output.write_text(json.dumps({'version':1,'outcome':outcome,'cases':results}),encoding='utf-8')
    print(outcome.upper())
    return 0 if outcome == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
