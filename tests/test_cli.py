import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
class CliTests(unittest.TestCase):
    def test_fixture_output_file(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"plan.json"
            p=subprocess.run([sys.executable,str(ROOT/"cli.py"),str(ROOT/"examples/scenario.json"),"--output",str(out)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr);self.assertIn("optimized",json.loads(out.read_text()))
    def test_invalid_input_exit_code(self):
        with tempfile.TemporaryDirectory() as d:
            bad=Path(d)/"bad.json";bad.write_text("{}")
            p=subprocess.run([sys.executable,str(ROOT/"cli.py"),str(bad)],capture_output=True,text=True)
            self.assertEqual(p.returncode,2);self.assertTrue(p.stderr.strip());self.assertEqual(p.stdout,"")
