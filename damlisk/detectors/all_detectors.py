from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.detectors.assets.stuck_asset import StuckAsset
from damlisk.detectors.authorization.controller_arg import ControllerFromArgument
from damlisk.detectors.authorization.delegated_leak import DelegatedLeak
from damlisk.detectors.authorization.hardcoded_party import HardcodedParty
from damlisk.detectors.authorization.over_disclosure import OverDisclosure
from damlisk.detectors.authorization.unprotected_archive import UnprotectedArchive
from damlisk.detectors.contracts.unsafe_primitive import UnsafePrimitive
from damlisk.detectors.hygiene.aborting_choice import AbortingChoice
from damlisk.detectors.hygiene.boolean_cst import BooleanConstant
from damlisk.detectors.hygiene.boolean_equal import BooleanEqual
from damlisk.detectors.hygiene.debug_trace import DebugTrace
from damlisk.detectors.hygiene.discarded_update import DiscardedUpdate
from damlisk.detectors.hygiene.rtlo import Rtlo
from damlisk.detectors.hygiene.tautological_compare import TautologicalCompare
from damlisk.detectors.hygiene.unused_field import UnusedTemplateField
from damlisk.detectors.upgrade.sdk_version import SdkVersion
from damlisk.detectors.validation.amount_tolerance import AmountTolerance
from damlisk.detectors.validation.divide_multiply import DivideBeforeMultiply
from damlisk.detectors.validation.hash_concat import HashConcatCollision
from damlisk.detectors.validation.missing_amount import MissingAmountCheck
from damlisk.detectors.validation.missing_ensure import MissingEnsure
from damlisk.detectors.validation.nonconsuming_create import NonconsumingCreate
from damlisk.detectors.validation.partial_function import PartialFunction
from damlisk.detectors.validation.time_argument import TimeFromArgument
from damlisk.detectors.validation.time_equality import TimeEquality
from damlisk.detectors.validation.unchecked_fetch import UncheckedFetch
from damlisk.detectors.validation.unconsumed_input import UnconsumedInput

DETECTORS: tuple[type[AbstractDetector], ...] = (
    BooleanConstant,
    BooleanEqual,
    ControllerFromArgument,
    MissingAmountCheck,
    UnusedTemplateField,
    HardcodedParty,
    PartialFunction,
    DiscardedUpdate,
    NonconsumingCreate,
    UncheckedFetch,
    TimeFromArgument,
    AmountTolerance,
    DivideBeforeMultiply,
    UnconsumedInput,
    AbortingChoice,
    HashConcatCollision,
    TimeEquality,
    TautologicalCompare,
    UnprotectedArchive,
    MissingEnsure,
    OverDisclosure,
    UnsafePrimitive,
    DebugTrace,
    StuckAsset,
    SdkVersion,
    Rtlo,
    DelegatedLeak,
)
