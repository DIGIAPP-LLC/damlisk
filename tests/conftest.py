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

from pathlib import Path

import pytest

from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex

ROOT = Path(__file__).parent.parent
BASELINE = (
    "splice-amulet-0.1.14",
    "splice-amulet-0.1.19",
    "splice-amulet-0.1.24",
    "splice-api-featured-app-v1-1.0.0",
    "splice-api-featured-app-v2-1.0.0",
    "splice-api-reward-assignment-v1-1.0.0",
    "splice-api-token-allocation-instruction-v1-1.0.0",
    "splice-api-token-allocation-instruction-v2-1.0.0",
    "splice-api-token-allocation-request-v2-1.0.0",
    "splice-api-token-allocation-v1-1.0.0",
    "splice-api-token-allocation-v2-1.0.0",
    "splice-api-token-holding-v1-1.0.0",
    "splice-api-token-metadata-v1-1.0.0",
    "splice-api-token-transfer-instruction-v1-1.0.0",
    "splice-api-token-transfer-instruction-v2-1.0.0",
    "splice-token-standard-utils-2.0.0",
    "splice-util-0.1.8",
    "splice-wallet-payments-0.1.24",
)
SPLICE_DARS = [ROOT / "examples" / "dars" / f"{name}.dar" for name in BASELINE]
AMULET_DAR = ROOT / "examples" / "dars" / "splice-amulet-0.1.24.dar"
BOOL_DAR = ROOT / "examples" / "vulnerable" / "boolean-cst" / "boolean-cst.dar"
EQ_DAR = ROOT / "examples" / "vulnerable" / "boolean-equal" / "boolean-equal.dar"
AMOUNT_DAR = ROOT / "examples" / "vulnerable" / "missing-amount-check" / "missing-amount-check.dar"
UNUSED_DAR = (
    ROOT / "examples" / "vulnerable" / "unused-template-field" / "unused-template-field.dar"
)
PARTY_DAR = ROOT / "examples" / "vulnerable" / "hardcoded-party" / "hardcoded-party.dar"
PARTIAL_DAR = ROOT / "examples" / "vulnerable" / "partial-function" / "partial-function.dar"
COPY_DAR = ROOT / "examples" / "vulnerable" / "nonconsuming-create" / "nonconsuming-create.dar"
FETCH_DAR = ROOT / "examples" / "vulnerable" / "unchecked-fetch" / "unchecked-fetch.dar"
TIME_DAR = ROOT / "examples" / "vulnerable" / "time-from-argument" / "time-from-argument.dar"
DIV_DAR = ROOT / "examples" / "vulnerable" / "divide-before-multiply" / "divide-before-multiply.dar"
HASH_DAR = ROOT / "examples" / "vulnerable" / "hash-concat-collision" / "hash-concat-collision.dar"
CLOCK_DAR = ROOT / "examples" / "vulnerable" / "time-equality" / "time-equality.dar"
SAME_DAR = ROOT / "examples" / "vulnerable" / "tautological-compare" / "tautological-compare.dar"
ARCHIVE_DAR = ROOT / "examples" / "vulnerable" / "unprotected-archive" / "unprotected-archive.dar"
DISCLOSE_DAR = ROOT / "examples" / "vulnerable" / "over-disclosure" / "over-disclosure.dar"
UNSAFE_DAR = ROOT / "examples" / "vulnerable" / "unsafe-primitive" / "unsafe-primitive.dar"
TRACE_DAR = ROOT / "examples" / "vulnerable" / "debug-trace" / "debug-trace.dar"
STUCK_DAR = ROOT / "examples" / "vulnerable" / "stuck-asset" / "stuck-asset.dar"
RTLO_DAR = ROOT / "examples" / "vulnerable" / "rtlo" / "rtlo.dar"
IFACE_DAR = (
    ROOT
    / "examples"
    / "vulnerable"
    / "untrusted-interface-exercise"
    / "untrusted-interface-exercise.dar"
)
DEPEND_DAR = ROOT / "examples" / "vulnerable" / "time-dependence" / "time-dependence.dar"
STALE_DAR = ROOT / "examples" / "vulnerable" / "stale-fetch" / "stale-fetch.dar"
OPTIONAL_DAR = ROOT / "examples" / "vulnerable" / "ignored-optional" / "ignored-optional.dar"
UNBOUNDED_DAR = (
    ROOT / "examples" / "vulnerable" / "unbounded-input-loop" / "unbounded-input-loop.dar"
)
LOOP_DAR = ROOT / "examples" / "vulnerable" / "ledger-op-in-loop" / "ledger-op-in-loop.dar"
RANDOM_DAR = ROOT / "examples" / "vulnerable" / "weak-randomness" / "weak-randomness.dar"
ARBITRARY_DAR = (
    ROOT / "examples" / "vulnerable" / "value-to-arbitrary-party" / "value-to-arbitrary-party.dar"
)
LEAK_DAR = (
    ROOT / "examples" / "vulnerable" / "delegated-authority-leak" / "delegated-authority-leak.dar"
)
ENSURE_DAR = ROOT / "examples" / "vulnerable" / "missing-ensure" / "missing-ensure.dar"
ABORT_DAR = ROOT / "examples" / "vulnerable" / "aborting-choice" / "aborting-choice.dar"
INPUT_DAR = ROOT / "examples" / "vulnerable" / "unconsumed-input" / "unconsumed-input.dar"
EPS_DAR = ROOT / "examples" / "vulnerable" / "amount-tolerance" / "amount-tolerance.dar"
DROP_DAR = ROOT / "examples" / "vulnerable" / "discarded-update" / "discarded-update.dar"
CTRL_DAR = (
    ROOT / "examples" / "vulnerable" / "controller-from-argument" / "controller-from-argument.dar"
)


@pytest.fixture(scope="session")
def amulet_index() -> PackageIndex:
    return PackageIndex(Dar.load(AMULET_DAR))


@pytest.fixture(scope="session")
def bool_index() -> PackageIndex:
    return PackageIndex(Dar.load(BOOL_DAR))


@pytest.fixture(scope="session")
def eq_index() -> PackageIndex:
    return PackageIndex(Dar.load(EQ_DAR))


@pytest.fixture(scope="session")
def ctrl_index() -> PackageIndex:
    return PackageIndex(Dar.load(CTRL_DAR))


@pytest.fixture(scope="session")
def amount_index() -> PackageIndex:
    return PackageIndex(Dar.load(AMOUNT_DAR))


@pytest.fixture(scope="session")
def unused_index() -> PackageIndex:
    return PackageIndex(Dar.load(UNUSED_DAR))


@pytest.fixture(scope="session")
def party_index() -> PackageIndex:
    return PackageIndex(Dar.load(PARTY_DAR))


@pytest.fixture(scope="session")
def partial_index() -> PackageIndex:
    return PackageIndex(Dar.load(PARTIAL_DAR))


@pytest.fixture(scope="session")
def drop_index() -> PackageIndex:
    return PackageIndex(Dar.load(DROP_DAR))


@pytest.fixture(scope="session")
def copy_index() -> PackageIndex:
    return PackageIndex(Dar.load(COPY_DAR))


@pytest.fixture(scope="session")
def fetch_index() -> PackageIndex:
    return PackageIndex(Dar.load(FETCH_DAR))


@pytest.fixture(scope="session")
def time_index() -> PackageIndex:
    return PackageIndex(Dar.load(TIME_DAR))


@pytest.fixture(scope="session")
def eps_index() -> PackageIndex:
    return PackageIndex(Dar.load(EPS_DAR))


@pytest.fixture(scope="session")
def div_index() -> PackageIndex:
    return PackageIndex(Dar.load(DIV_DAR))


@pytest.fixture(scope="session")
def input_index() -> PackageIndex:
    return PackageIndex(Dar.load(INPUT_DAR))


@pytest.fixture(scope="session")
def abort_index() -> PackageIndex:
    return PackageIndex(Dar.load(ABORT_DAR))


@pytest.fixture(scope="session")
def hash_index() -> PackageIndex:
    return PackageIndex(Dar.load(HASH_DAR))


@pytest.fixture(scope="session")
def clock_index() -> PackageIndex:
    return PackageIndex(Dar.load(CLOCK_DAR))


@pytest.fixture(scope="session")
def same_index() -> PackageIndex:
    return PackageIndex(Dar.load(SAME_DAR))


@pytest.fixture(scope="session")
def archive_index() -> PackageIndex:
    return PackageIndex(Dar.load(ARCHIVE_DAR))


@pytest.fixture(scope="session")
def ensure_index() -> PackageIndex:
    return PackageIndex(Dar.load(ENSURE_DAR))


@pytest.fixture(scope="session")
def disclose_index() -> PackageIndex:
    return PackageIndex(Dar.load(DISCLOSE_DAR))


@pytest.fixture(scope="session")
def unsafe_index() -> PackageIndex:
    return PackageIndex(Dar.load(UNSAFE_DAR))


@pytest.fixture(scope="session")
def trace_index() -> PackageIndex:
    return PackageIndex(Dar.load(TRACE_DAR))


@pytest.fixture(scope="session")
def stuck_index() -> PackageIndex:
    return PackageIndex(Dar.load(STUCK_DAR))


@pytest.fixture(scope="session")
def rtlo_index() -> PackageIndex:
    return PackageIndex(Dar.load(RTLO_DAR))


@pytest.fixture(scope="session")
def leak_index() -> PackageIndex:
    return PackageIndex(Dar.load(LEAK_DAR))


@pytest.fixture(scope="session")
def depend_index() -> PackageIndex:
    return PackageIndex(Dar.load(DEPEND_DAR))


@pytest.fixture(scope="session")
def random_index() -> PackageIndex:
    return PackageIndex(Dar.load(RANDOM_DAR))


@pytest.fixture(scope="session")
def loop_index() -> PackageIndex:
    return PackageIndex(Dar.load(LOOP_DAR))


@pytest.fixture(scope="session")
def unbounded_index() -> PackageIndex:
    return PackageIndex(Dar.load(UNBOUNDED_DAR))


@pytest.fixture(scope="session")
def stale_index() -> PackageIndex:
    return PackageIndex(Dar.load(STALE_DAR))


@pytest.fixture(scope="session")
def arbitrary_index() -> PackageIndex:
    return PackageIndex(Dar.load(ARBITRARY_DAR))


@pytest.fixture(scope="session")
def iface_index() -> PackageIndex:
    return PackageIndex(Dar.load(IFACE_DAR))


@pytest.fixture(scope="session")
def optional_index() -> PackageIndex:
    return PackageIndex(Dar.load(OPTIONAL_DAR))
