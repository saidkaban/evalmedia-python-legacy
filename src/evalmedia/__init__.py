"""evalmedia — Evaluate AI-generated media quality."""

__version__ = "0.1.1"

from evalmedia.config import set_judge
from evalmedia.core import CheckResult, CheckStatus, CompareResult, EvalResult
from evalmedia.eval import ImageEval, compare
from evalmedia.image_utils import ImageInput

__all__ = [
    "CheckResult",
    "CheckStatus",
    "CompareResult",
    "EvalResult",
    "ImageEval",
    "ImageInput",
    "compare",
    "set_judge",
]
