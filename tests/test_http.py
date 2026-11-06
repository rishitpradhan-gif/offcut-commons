import json,threading,unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from pathlib import Path
from server import Handler
class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.url='http://127.0.0.1:'+str(cls.server.server_port)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def post(self,data,headers=None):
        request=Request(self.url+'/api/solve',data=json.dumps(data).encode(),headers={'Content-Type':'application/json',**(headers or {})})
        return urlopen(request)
    def test_health_and_static(self):
        with urlopen(self.url+'/api/health') as r:self.assertEqual(json.load(r)['status'],'ok')
        with urlopen(self.url+'/') as r:self.assertIn('Content-Security-Policy',r.headers);self.assertIn(b'<canvas',r.read())
    def test_example_solves_over_http(self):
        with urlopen(self.url+'/api/sample') as r:s=json.load(r)
        with self.post(s) as r:self.assertIn('optimized',json.load(r))
    def test_invalid_scenario_returns_400(self):
        with self.assertRaises(HTTPError) as e:self.post({})
        self.assertEqual(e.exception.code,400)
    def test_cross_origin_denied(self):
        with self.assertRaises(HTTPError) as e:self.post({}, {'Origin':'https://untrusted.example'})
        self.assertEqual(e.exception.code,403)
    def test_unknown_files_not_served(self):
        for path in ['/engine.py','/../LICENSE','/web/../../server.py']:
            with self.subTest(path=path),self.assertRaises(HTTPError) as e:urlopen(self.url+path)
            self.assertEqual(e.exception.code,404)
