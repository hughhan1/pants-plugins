from typing import Iterable

from pants.engine.rules import Rule

import ariadne.dependency_inference.rules as dependency_inference_rules
from ariadne.goals import tailor


def rules() -> Iterable[Rule]:
    return [*dependency_inference_rules.rules(), *tailor.rules()]
