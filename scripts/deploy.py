#!/usr/bin/env python3
"""Package a versioned zip, or upload the runtime tree to PythonAnywhere and reload.

PythonAnywhere cannot run pip over the API, so Flask must already be installed
in the webapp virtualenv (one-time). This script replaces source files and
reloads.
"""

from __future__ import annotations

import argparse
import os
import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = (
    "app.py",
    "transliterate.py",
    "plugins/__init__.py",
    "plugins/cyrillic.py",
    "plugins/greek.py",
    "wsgi.py",
    "pyproject.toml",
    "requirements.txt",
    "data/puzzles.json",
    "data/practice.json",
    "static/app.js",
    "static/style.css",
    "templates/index.html",
)


def version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as f:
        return tomllib.load(f)["project"]["version"]


def package(dist_dir: Path) -> Path:
    dist_dir.mkdir(exist_ok=True)
    zpath = dist_dir / f"transliterillic-{version()}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in RUNTIME_FILES:
            zf.write(ROOT / rel, rel)
    print(f"wrote {zpath}")
    return zpath


def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if not value:
        raise SystemExit(f"missing environment variable {name}")
    return value


def _api(session, site: str, username: str, method: str, path: str, **kwargs):
    import requests

    url = f"https://{site}/api/v0/user/{username}{path}"
    response = session.request(method, url, timeout=60, **kwargs)
    if not response.ok:
        raise SystemExit(f"{method} {path} -> {response.status_code}: {response.text[:500]}")
    return response


def deploy() -> None:
    import requests

    token = _env("API_TOKEN")
    username = _env("PYTHONANYWHERE_USERNAME")
    site = os.environ.get("PYTHONANYWHERE_SITE") or "www.pythonanywhere.com"
    default_domain = (
        f"{username}.eu.pythonanywhere.com"
        if site.startswith("eu.")
        else f"{username}.pythonanywhere.com"
    )
    domain = os.environ.get("PYTHONANYWHERE_DOMAIN") or default_domain
    project = os.environ.get("PYTHONANYWHERE_PROJECT_DIR") or f"/home/{username}/transliterillic"
    venv = os.environ.get("PYTHONANYWHERE_VENV") or f"/home/{username}/.virtualenvs/transliterillic"
    python_version = os.environ.get("PYTHONANYWHERE_PYTHON") or "python313"

    session = requests.Session()
    session.headers["Authorization"] = f"Token {token}"

    for rel in RUNTIME_FILES:
        remote = f"{project}/{rel}"
        print(f"upload {rel} -> {remote}")
        with (ROOT / rel).open("rb") as fh:
            _api(
                session,
                site,
                username,
                "POST",
                f"/files/path{remote}",
                files={"content": fh},
            )

    wsgi_name = domain.replace(".", "_")
    wsgi_path = f"/var/www/{wsgi_name}_wsgi.py"
    wsgi = (
        "import sys\n"
        f"project = {project!r}\n"
        "if project not in sys.path:\n"
        "    sys.path.insert(0, project)\n"
        "from app import app as application\n"
    )
    print(f"upload wsgi -> {wsgi_path}")
    _api(
        session,
        site,
        username,
        "POST",
        f"/files/path{wsgi_path}",
        files={"content": ("wsgi.py", wsgi.encode("utf-8"))},
    )

    info = session.get(f"https://{site}/api/v0/user/{username}/webapps/{domain}/", timeout=60)
    if info.status_code == 404:
        print(f"create webapp {domain} ({python_version})")
        _api(
            session,
            site,
            username,
            "POST",
            "/webapps/",
            data={"domain_name": domain, "python_version": python_version},
        )
    elif not info.ok:
        raise SystemExit(f"GET /webapps/{domain}/ -> {info.status_code}: {info.text[:500]}")

    _api(
        session,
        site,
        username,
        "PATCH",
        f"/webapps/{domain}/",
        data={"source_directory": project, "virtualenv_path": venv},
    )

    mappings = _api(session, site, username, "GET", f"/webapps/{domain}/static_files/").json()
    if not isinstance(mappings, list):
        mappings = []
    static_urls = {item.get("url") for item in mappings}
    if "/static/" not in static_urls and "/static" not in static_urls:
        print("map /static/ ->", f"{project}/static")
        _api(
            session,
            site,
            username,
            "POST",
            f"/webapps/{domain}/static_files/",
            json={"url": "/static/", "path": f"{project}/static"},
        )

    print(f"reload {domain}")
    reload = session.post(
        f"https://{site}/api/v0/user/{username}/webapps/{domain}/reload/",
        timeout=60,
    )
    if reload.status_code == 409:
        print("reload returned 409 (often a custom-domain CNAME warning); treating as ok")
    elif not reload.ok:
        raise SystemExit(f"reload -> {reload.status_code}: {reload.text[:500]}")
    print(f"deployed v{version()} to {domain}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("package", "pythonanywhere"))
    args = parser.parse_args()
    if args.command == "package":
        package(ROOT / "dist")
    else:
        deploy()


if __name__ == "__main__":
    sys.exit(main())
