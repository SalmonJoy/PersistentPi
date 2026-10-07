"""Local research CLI; never exposed as an agent tool."""
import argparse
import json
from pathlib import Path
import sqlite3

from .config import resolve
from .experiments import ExperimentManager, summary
from .export import export


def main(argv=None):
    parser = argparse.ArgumentParser(prog='persistentpi')
    parser.add_argument('--state', type=Path, default=Path('.local/default'))
    commands = parser.add_subparsers(dest='command', required=True)
    run = commands.add_parser('run')
    run.add_argument('--config', type=Path, required=True)
    run.add_argument('--formal', action='store_true')
    run.add_argument('--replicate', type=int)
    status = commands.add_parser('status')
    status.add_argument('--run')
    stop = commands.add_parser('stop')
    stop.add_argument('--run', required=True)
    exporting = commands.add_parser('export')
    exporting.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    manager = None
    try:
        resolved = resolve(args.config, mode='formal' if args.formal else 'development',
                           replicate=args.replicate) if args.command == 'run' else None
        manager = ExperimentManager(args.state)
        if args.command == 'run':
            rows = manager.run(resolved)
            result = [summary(row) for row in rows]
        elif args.command == 'status':
            result = [summary(row) for row in manager.status(args.run)]
        elif args.command == 'stop':
            result = {'run_id': args.run, 'requested': manager.store.request_stop(args.run)}
        else:
            manager.status()
            result = export(manager, args.output)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ValueError, KeyError, OSError, sqlite3.Error) as exc:
        parser.exit(2, 'persistentpi: ' + str(exc) + '\n')
    finally:
        if manager:
            manager.close()
