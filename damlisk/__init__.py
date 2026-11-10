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

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version
from pathlib import Path as _Path

_hash_file = _Path(__file__).parent.joinpath("damlisk_git_commithash.txt")

if _hash_file.exists():
    with _hash_file.open() as fp:
        __commit__ = fp.read()
else:
    __commit__ = "unknown"

__version__: str
try:
    __version__ = _version("damlisk")
except PackageNotFoundError:
    from damlisk.version import version

    __version__ = version

__long_version__ = f"{__version__}+commit.{__commit__}"
