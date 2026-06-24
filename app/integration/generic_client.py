"""
Generic REST Client Wrapper
Module 7: Generics
"""

from typing import TypeVar, Generic, Dict, Any, List, Type, Optional

T = TypeVar('T')

class GenericClient(Generic[T]):
    """
    Generic HTTP client wrapper class.
    """
    def __init__(self, base_url: str, model_class: Optional[Type[T]] = None):
        self.base_url = base_url
        self.model_class = model_class

    def parse_response(self, response_data: Dict[str, Any]) -> T:
        """Parse raw dictionary to T."""
        if self.model_class is not None:
            if hasattr(self.model_class, "model_validate"):
                return self.model_class.model_validate(response_data)
            elif hasattr(self.model_class, "parse_obj"):
                return self.model_class.parse_obj(response_data)
            return self.model_class(**response_data)
        return response_data

    def parse_list_response(self, response_list: List[Dict[str, Any]]) -> List[T]:
        """Parse list of raw dictionaries to list of T."""
        return [self.parse_response(item) for item in response_list]
