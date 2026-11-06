import copy,itertools,json,math,unittest
from pathlib import Path
from unittest.mock import patch
from engine import solve,tour
SAMPLE=json.loads((Path(__file__).parents[1]/"examples/scenario.json").read_text())
class ReuseTests(unittest.TestCase):
    def test_every_cut_placed_once(self):
        r=solve(SAMPLE)['optimized'];cuts=[c for p in r['patterns'] for c in p['cuts']]
        self.assertEqual(len(cuts),sum(d['quantity'] for d in SAMPLE['demand']))
        self.assertCountEqual([c['length_mm'] for c in cuts],[d['length_mm'] for d in SAMPLE['demand'] for _ in range(d['quantity'])])
    def test_no_stock_overdraw_and_kerf_conserved(self):
        r=solve(SAMPLE)['optimized'];self.assertAlmostEqual(r['cut_mm']+r['kerf_mm']+r['leftover_mm'],r['stock_mm'])
        for p in r['patterns']:self.assertGreaterEqual(p['remaining_mm'],0)
    def test_sample_improves_joint_objective(self):
        r=solve(SAMPLE);self.assertLess(r['optimized']['objective'],r['baseline']['objective']);self.assertTrue(r['search_complete'])
    def test_tour_matches_permutations(self):
        points=[[1,2],[4,1],[3,5],[0,4]];origin=[0,0];cost,order=tour(points,origin)
        brute=min(sum(math.dist(a,b) for a,b in zip([origin]+list(p),list(p)+[origin])) for p in itertools.permutations(points))
        self.assertAlmostEqual(cost,brute);self.assertEqual(sorted(order),list(range(4)))
    def test_kerf_makes_exact_fit_infeasible(self):
        s={'origin':[0,0],'suppliers':[{'id':'a','position':[0,1]}],'stock':[{'id':'s','length_mm':1000,'material':'x','supplier':'a','cost':1}],'demand':[{'length_mm':500,'quantity':2,'material':'x'}],'kerf_mm':1}
        with self.assertRaises(ValueError):solve(s)
        s['kerf_mm']=0;self.assertEqual(solve(s)['optimized']['leftover_mm'],0)
    def test_material_incompatibility(self):
        s=copy.deepcopy(SAMPLE);s['demand'][0]['material']='incompatible'
        with self.assertRaises(ValueError):solve(s)
    def test_tiny_assignment_matches_exhaustive_cost(self):
        s={'origin':[0,0],'suppliers':[{'id':'a','position':[0,1]},{'id':'b','position':[1,0]}],'stock':[{'id':'a','length_mm':1400,'cost':2,'material':'x','supplier':'a'},{'id':'b','length_mm':2400,'cost':4,'material':'x','supplier':'b'}],'demand':[{'length_mm':600,'quantity':2,'material':'x'}],'kerf_mm':3,'waste_cost_per_meter':2,'travel_cost_per_km':1}
        scores=[]
        for assignments in itertools.product(range(2),repeat=2):
            used=set(assignments)
            if any(assignments.count(i)*603>s['stock'][i]['length_mm'] for i in used):continue
            cost=sum(s['stock'][i]['cost'] for i in used);left=sum(s['stock'][i]['length_mm'] for i in used)-1206;km=tour([s['suppliers'][i]['position'] for i in sorted(used)],[0,0])[0];scores.append(cost+left*.002+km)
        self.assertAlmostEqual(solve(s)['optimized']['objective'],min(scores),places=5)
    def test_search_cap_is_reported(self):
        with patch('engine.SEARCH_LIMIT',1):
            r=solve(SAMPLE);self.assertFalse(r['search_complete']);self.assertIsNotNone(r['optimized'])
    def test_invalid_inputs(self):
        for patch_data in [{'kerf_mm':-1},{'travel_cost_per_km':float('inf')},{'demand':[{'length_mm':400,'quantity':17,'material':'x'}]},{'origin':[True,0]}]:
            with self.subTest(patch=patch_data),self.assertRaises(ValueError):solve({**SAMPLE,**patch_data})
