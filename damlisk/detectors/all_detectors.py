from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.detectors.authorization.controller_arg import ControllerFromArgument
from damlisk.detectors.authorization.hardcoded_party import HardcodedParty
from damlisk.detectors.hygiene.boolean_cst import BooleanConstant
from damlisk.detectors.hygiene.boolean_equal import BooleanEqual
from damlisk.detectors.hygiene.discarded_update import DiscardedUpdate
from damlisk.detectors.hygiene.unused_field import UnusedTemplateField
from damlisk.detectors.validation.missing_amount import MissingAmountCheck
from damlisk.detectors.validation.nonconsuming_create import NonconsumingCreate
from damlisk.detectors.validation.partial_function import PartialFunction
from damlisk.detectors.validation.unchecked_fetch import UncheckedFetch

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
)
