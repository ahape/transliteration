# Transliteration

## Background

**100% vibe-coded using Grok 4.6 (high)**. Most of the work done is based off of a single wireframe and prompt. UI adjustments and CI/CD cruft added in subsequent prompts.

Original [wireframe](https://imgur.com/a/eSq1aQo)

<details>
<summary>Original prompt</summary>

> Create a web app based on the `wireframe.jpg` photo. Use a minimal Flask backend and choose the simplest front-end technology for you to maintain. Use IndexedDB or `localStorage` for persistence if needed.

> The app should include a daily puzzle system similar to Wordle: each user can complete one scored solve per day, while still being able to browse and practice previous or other words without affecting their score.

> Each daily puzzle should contain three words. All words must come from a valid Scrabble word list, so they should be relatively short and must not include proper nouns. Pre-generate and store a fixed sequence of daily word sets for at least the next 500 days, ensuring that every user worldwide receives the same three words on a given date.

> The words to solve should be English words transliterated into Cyrillic, rather than words native to the particular Cyrillic-language variant used in the app.

</details>

A daily three-word puzzle: an English Scrabble word, shown in Cyrillic or Greek. New word every day.

One-liner copy/pasta
```bash
uv venv --clear && source .venv/bin/activate && uv pip install -r requirements.txt && flask --app app run --port 5005
```

Multiline copy/pasta
```bash
uv venv --clear
source .venv/bin/activate
uv pip install -r requirements.txt
flask --app app run --port 5005
```

`pip install pytest` then `pytest` to run the test suite.

Version is the `version` field in `pyproject.toml`.

## Deploying

### PythonAnywhere

First, in "Consoles", enter a Bash console and see which python versions you have access to:

```bash
ls /usr/bin/python3.*
```

Python `>3.10` is only on the **innit** system image (Account → System image). Older images stop around 3.10.

Then, using whichever version supported:

```bash
mkvirtualenv transliterillic --python=python3.XX
pip install 'flask>=3.0'
```

Web tab: add a **Manual configuration** app with **the same** Python version.

* Virtualenv = `/home/<you>/.virtualenvs/transliterillic`
* Source = `/home/<you>/transliterillic`.

Those host paths are the live PythonAnywhere layout. Leave them as-is unless you recreate the webapp; `scripts/deploy.py` still defaults to them.

When finished, reload the website.

### GitHub Actions

CI runs tests on every push. A versioned zip is attached as a workflow artifact. Deploy happens on a `v*` tag or a manual **Run workflow**.

If the GitHub deploy job creates the webapp, set variable `PYTHONANYWHERE_PYTHON` to match (`python310`, `python311`, `python312`, …).

GitHub repo **Settings → Secrets and variables → Actions** (repository secrets/variables):

| Secret / variable | Required | Example |
|---|---|---|
| `PYTHONANYWHERE_API_TOKEN` (secret) | yes | from Account → API token |
| `PYTHONANYWHERE_USERNAME` (secret) | yes | your PA username |
| `PYTHONANYWHERE_DOMAIN` (variable) | no | `you.pythonanywhere.com` |
| `PYTHONANYWHERE_SITE` (variable) | no | `www.pythonanywhere.com` or `eu.pythonanywhere.com` |
| `PYTHONANYWHERE_PYTHON` (variable) | no | `python3XX` (otherwise 3.13) |

### GitHub Actions &gt; Releasing

```bash
VER="v$(uv version --bump patch | sed -E 's/.*=>[[:space:]]*//')"
git commit -i pyproject.toml -i uv.lock -m "Release $VER"
git tag -a $VER -m "Release $VER"
git push origin $VER
```

Or **Actions → CI → Run workflow**. The API uploads the runtime files and reloads the webapp; it cannot `pip install` for you, so extra Python deps still need the console.

