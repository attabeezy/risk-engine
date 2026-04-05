"""
Utility functions for input validation.
"""

import math
from typing import Union


def validate_positive(value: Union[int, float], name: str) -> float:
    """
    Validate that a value is positive and finite.

    Args:
        value: Numeric value to validate
        name: Name of the parameter for error message

    Returns:
        The validated value as float

    Raises:
        ValueError: If value is not positive
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value)}")
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite, got {value}")
    return float(value)


def validate_non_negative(value: Union[int, float], name: str) -> float:
    """
    Validate that a value is non-negative and finite.

    Args:
        value: Numeric value to validate
        name: Name of the parameter for error message

    Returns:
        The validated value as float

    Raises:
        ValueError: If value is negative
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value)}")
    if value < 0:
        raise ValueError(f"{name} cannot be negative, got {value}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite, got {value}")
    return float(value)
