from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.detectors.authorization.controller_arg import ControllerFromArgument
from damlisk.detectors.hygiene.boolean_cst import BooleanConstant
from damlisk.detectors.hygiene.boolean_equal import BooleanEqual

DETECTORS: tuple[type[AbstractDetector], ...] = (
    BooleanConstant,
    BooleanEqual,
    ControllerFromArgument,
)
