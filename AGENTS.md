# Project guidance

Keep the pure engine separate from HTTP and visualization code. Python 3.10+ standard library is the runtime baseline. Preserve input limits and loopback binding. Do not introduce hardware actuation, external network services, or claims of measured outcomes into the default demo.

Run `python3 -m unittest discover -s tests -v` before publishing changes. Add a small exact or brute-force comparison for optimization changes. Label synthetic examples and incomplete search results explicitly. Screenshots in `docs/` must show the current implementation.
