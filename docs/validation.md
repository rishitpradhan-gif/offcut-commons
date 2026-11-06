# Validation

Verified locally on November 5, 2026 with Python 3.12 and Chrome.

- Engine tests cover constraints, invalid inputs, and comparison against an exact tiny case.
- HTTP tests exercise example solving, invalid scenarios, static-file allowlisting, and cross-origin rejection.
- CLI tests verify file output and nonzero failure exits.
- Browser checks exercised solver controls, result export, invalid JSON handling, and a 390px mobile viewport with no horizontal page overflow or uncaught page errors.
- Desktop and mobile screenshots in this directory show the included synthetic example.

Run the automated Python suite with `python3 -m unittest discover -s tests -v`. A GitHub Actions template is included in `ci/github-actions-test.yml`; it is not active until installed with workflow-authorized credentials. The UI browser checks were run against the local app; hardware integrations and field performance have not been tested.
