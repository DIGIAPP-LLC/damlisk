from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.detectors.hygiene.boolean_cst import BooleanConstant

DETECTORS: tuple[type[AbstractDetector], ...] = (BooleanConstant,)
