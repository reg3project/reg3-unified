"""REG3 Learn Module - Pattern learning and correction application."""

from .pattern_learner import PatternLearner, learn_patterns
from .correction_applier import CorrectionApplier, apply_corrections

__all__ = [
    'PatternLearner',
    'learn_patterns',
    'CorrectionApplier',
    'apply_corrections',
]
