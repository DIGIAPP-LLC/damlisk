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

import os
import re
import subprocess

from setuptools import find_packages, setup

long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()


def _local_version(version):
    return ""


def _global_version(version):
    from setuptools_scm.version import guess_next_dev_version

    return re.sub(r"\.dev\d+", "", guess_next_dev_version(version))


hash_file_rel_path = os.path.join("damlisk", "damlisk_git_commithash.txt")
hashfile = os.path.relpath(hash_file_rel_path)

try:
    commithash = subprocess.check_output("git rev-parse --short HEAD".split())
    with open(hashfile, "w") as fh:
        fh.write(commithash.decode("utf-8").strip())
except subprocess.CalledProcessError:
    pass


setup(
    name="damlisk",
    use_scm_version={
        "local_scheme": _local_version,
        "version_scheme": _global_version,
        "write_to": "damlisk/version.py",
        "fallback_version": "0.0.0.dev0",
    },
    description="Damlisk: static analyzer for Daml-LF packages (.dar)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DIGIAPP LLC",
    author_email="artem@kekpool.com",
    maintainer="DIGIAPP LLC",
    url="https://github.com/DIGIAPP-LLC/damlisk",
    keywords="daml canton daml-lf static analysis security",
    include_package_data=False,
    packages=find_packages(include=["damlisk", "damlisk.*"]),
    python_requires=">=3.11,<4",
    setup_requires=["setuptools_scm>=7.1.0,<8.0.0"],
    entry_points={"console_scripts": ["damlisk=damlisk.cli.main:cli"]},
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    data_files=[("", [hash_file_rel_path])],
)
