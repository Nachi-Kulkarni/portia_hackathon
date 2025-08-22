"""
Compatibility fix for Python 3.11 with Portia SDK

The Portia SDK requires 'override' from typing, which is only available in Python 3.12+.
This module patches the typing module to include override from typing_extensions.
"""

import typing
from typing_extensions import override

# Monkey-patch typing module to include override for Python < 3.12
if not hasattr(typing, 'override'):
    typing.override = override
    # Also add to typing.__all__ if it exists
    if hasattr(typing, '__all__'):
        typing.__all__.append('override')

# Ensure the override is accessible
__all__ = ['override']