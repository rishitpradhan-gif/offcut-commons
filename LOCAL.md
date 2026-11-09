# Run Offcut Commons locally

Cutting-stock planning combined with supplier pickup routing.

**[Download the ready-to-run ZIP](https://github.com/rishitpradhan-gif/offcut-commons/releases/download/local-v1/offcut-commons-local.zip)** · [All tools](https://github.com/rishitpradhan-gif/rishitpradhan-gif/blob/main/TOOLS.md)

## Three steps

1. Install Python 3.10+ if it is not already on your computer.
2. Download the ZIP above, **extract all files**, and open a terminal in the extracted folder (the one containing server.py).
3. Run:

```sh
python3 server.py
```

Open http://127.0.0.1:4313 in a modern browser.

Python 3.10+. No pip packages, API keys, or accounts are needed.

Keep the terminal open while using a server. Press **Ctrl+C** to stop it. Research verifiers exit after finishing their checks.

## If you get stuck

- **Windows:** replace `python3` with `py -3` in Python commands. If neither works, install Python from [python.org](https://www.python.org/downloads/). For the APIs, install Node from [nodejs.org](https://nodejs.org/en/download).
- **“File not found”:** extract the ZIP first, then change into the inner folder containing the launcher. Do not run from inside the ZIP viewer.
- **“Command not found”:** check `python3 --version` / `py -3 --version`, or `node --version` for the APIs. Reopen the terminal after installing a runtime.
- **Port already in use:** run `python3 server.py --port 8001` and open http://127.0.0.1:8001 instead.

## Use the API or command line

POST scenario JSON to `/api/solve`, or run:

```sh
python3 cli.py examples/scenario.json --output plan.json
```

The local server keeps scenarios in memory. Export results you want to retain. See README.md for model assumptions and limits.

These downloads run locally. The local servers bind to your own computer; they are not configured as public multi-user services.
