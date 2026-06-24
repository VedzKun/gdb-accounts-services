"""
Security & PIN Encapsulation Utility
Module 4: Thinking in Objects & OO Programming
"""

class BaseSecurity:
    """Base security provider handling raw encryption/decryption keys."""
    
    def __init__(self, encryption_key: str):
        # Private field using double underscore (name mangled in Python)
        self._secret_key = encryption_key

    def get_key_length(self) -> int:
        """Return length of key."""
        return len(self._secret_key)


class AccountSecurity(BaseSecurity):
    """Specific account security helper class."""
    
    def __init__(self, encryption_key: str, salt: str):
        super().__init__(encryption_key)
        self.salt = salt

    def generate_masked_key(self) -> str:
        """
        Generate a masked key string for UI display.
        
        Bug (M04-Bug-01):
        Attempting to access double-underscore private field from parent class directly.
        In Python, `__secret_key` in BaseSecurity is name-mangled to `_BaseSecurity__secret_key`,
        so accessing `self.__secret_key` raises AttributeError: 'AccountSecurity' object has no attribute '_AccountSecurity__secret_key'.
        
        Trainees must change `__secret_key` to a protected field `_secret_key` or provide a public getter.
        """
        # TODO: [M04-Bug-01] BUG: Generating masked keys crashes. The subclass seems unable to access a property from its parent.
        raw_key = self._secret_key  # Raises AttributeError
        return f"MASKED-{raw_key[:4]}-{self.salt}"


# ============================================================================
# CR (M04-CR-01): PIN Encapsulation with Properties
# ============================================================================
# TODO:
# 1. Define a class `PinEncapsulator` that hides the raw 4-digit PIN in a private field `_pin`.
# 2. Implement a `@property` getter for `pin` that returns a masked string (e.g. "**34" or "XXXX").
# 3. Implement a `@pin.setter` that verifies the PIN is a 4-digit numeric string, otherwise raises ValueError.

# TODO: [M04-CR-01] FEATURE: Implement proper encapsulation for the PIN field using decorators for getters and setters.
class PinEncapsulator:
    """
    Class providing encapsulation and masking for account PINs.
    """
    def __init__(self, initial_pin: str):
        self.pin = initial_pin

    @property
    def pin(self) -> str:
        """Get the masked PIN representation."""
        if not hasattr(self, "_pin") or not self._pin:
            return ""
        return "**" + self._pin[-2:]

    @pin.setter
    def pin(self, value: str) -> None:
        """Set the PIN value after validation."""
        if not isinstance(value, str):
            raise ValueError("PIN must be a string")
        if not value.isdigit() or len(value) != 4:
            raise ValueError("PIN must be a 4-digit numeric string")
        self._pin = value
