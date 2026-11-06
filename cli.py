"""Solve a scenario file without starting the web server."""
import argparse,json,sys
from pathlib import Path
from engine import solve

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenario',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        data=json.loads(args.scenario.read_text())
        if not isinstance(data,dict):raise ValueError('Scenario must be an object')
        result=json.dumps(solve(data),indent=2,allow_nan=False)+'\n'
        if args.output:args.output.write_text(result)
        else:sys.stdout.write(result)
    except (OSError,ValueError,TypeError,KeyError,IndexError) as e:
        print(str(e),file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
