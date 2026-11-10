# Copyright 2026 DIGIAPP LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import os
import shutil
import ssl
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

try:
    from certifi import where

    CAFILE: str | None = where()
except ImportError:
    CAFILE = None

API = "https://api.github.com/repos/canton-network/splice/contents/daml/dars"
TLS = ssl.create_default_context(cafile=CAFILE)


@dataclass(frozen=True)
class Dar:
    name: str
    url: str
    size: int


def list_dars(ref: str) -> list[Dar]:
    """Return every DAR published in the Splice repository at `ref`."""
    req = urllib.request.Request(f"{API}?ref={ref}")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, context=TLS) as resp:
        items = json.load(resp)
    dars = []
    for item in items:
        if item["name"].endswith(".dar"):
            dars.append(Dar(item["name"], item["download_url"], item["size"]))
    return dars


def wanted(dar: Dar, prefixes: list[str]) -> bool:
    """Return True if no prefixes are given or the DAR name starts with one of them."""
    if not prefixes:
        return True
    for prefix in prefixes:
        if dar.name.startswith(prefix):
            return True
    return False


def fetch(dar: Dar, out: Path) -> bool:
    """Download `dar` into `out` unless a file of the same size is there; return True if fetched."""
    path = out / dar.name
    if path.exists() and path.stat().st_size == dar.size:
        return False
    tmp = path.with_suffix(".part")
    with urllib.request.urlopen(dar.url, context=TLS) as resp, tmp.open("wb") as fh:
        shutil.copyfileobj(resp, fh)
    tmp.replace(path)
    return True


def main() -> int:
    """Download Splice DARs from the official repository into a folder."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--out", default="examples/dars", help="target folder")
    parser.add_argument("--ref", default="main", help="Splice branch or tag")
    parser.add_argument("--only", default="", help="comma-separated name prefixes")
    parser.add_argument("--list", action="store_true", help="only print available DARs")
    args = parser.parse_args()
    prefixes = [part for part in args.only.split(",") if part]
    found = list_dars(args.ref)
    dars = [dar for dar in found if wanted(dar, prefixes)]
    if args.list:
        for dar in dars:
            print(dar.name)
        return 0
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    got = 0
    for dar in dars:
        if fetch(dar, out):
            got += 1
            print(f"fetched {dar.name}")
    print(f"{got} fetched, {len(dars) - got} up to date, in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
