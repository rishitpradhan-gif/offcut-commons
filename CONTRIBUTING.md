# Contributing

Run the sample, read the model assumptions in the README, and open an issue with a small reproducible scenario. For algorithm changes, add a regression test and compare against a brute-force solution on a tiny case when practical. Keep the core dependency-free and separate measured data from illustrative fixtures.

Run `python3 -m unittest discover -s tests -v` before proposing a change. Do not add network calls or hardware actuation to the default demo. Contributions are licensed under this repository's MIT license.
