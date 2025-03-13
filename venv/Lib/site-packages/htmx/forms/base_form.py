from typing import Any, Callable, Dict, Generic, List, Literal, Optional, Type, TypeVar

from nicegui import ui
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class FormError(Exception):
    """Form Error."""

    def __init__(self, message: str):
        """Form Exception."""
        super().__init__(message)


class BaseForm(Generic[T]):
    """
    Base Form.

    This is the base form class that all forms should inherit from.
    """

    Model: Type[T]
    OnCallbackEvent = Callable[[Any], Any]
    OnEventLiteral = Literal["submit"]
    default_data: T
    _on_events: Dict[str, List[OnCallbackEvent]]
    _data: T
    _form_valid: bool
    _ui_inputs: List[ui.input]
    _ui_submit_trigger: Callable[[], Any]

    # TODO: Figure out how to type this, instead of Dict[str, Any], it needs to be the allowed Model fields
    def __init__(self, data: Optional[T | Dict[str, Any]] = None):
        """
        Initialize the form.

        :param data: The data to use for the form. Defaults to None
        """
        if not hasattr(self, "Model"):
            raise FormError("Model not defined")

        if isinstance(data, dict):
            data = self.Model.construct(**data)

        if not hasattr(self, "default_data"):
            self.default_data = self.Model.construct(**self.Model().dict())

        if data is None:
            data = self.default_data.copy()

        self._data = data
        self._ui_inputs = []
        self._on_events = {
            "submit": [],
        }
        self._form_valid = False

    def get_value(self, *names: str) -> Any:
        """
        Get the value of a field.

        :param names: The names of the fields to get the value of
        """
        current_obj = self._data

        for name in names:
            current_obj = getattr(current_obj, name, None)

            if current_obj is None:
                break

        return current_obj

    def set_value(self, value: Any, *names: str) -> None:
        """
        Set the value of a field.

        :param value: The value to set
        """
        current_obj = self._data

        for name in names[:-1]:
            current_obj = getattr(current_obj, name, None)

            if current_obj is None:
                raise FormError(f"Invalid field name: {name}")

        setattr(current_obj, names[-1], value)

    def data(self):
        """
        Get the model data.

        :return: The model data as a dict
        """
        return self._data.dict()

    def set_data(self, data: T | Dict[str, Any]) -> None:
        """
        Set the model data.

        :param data: The data to set
        """
        # If data responds to dict(), then it is a model
        if hasattr(data, "dict"):
            data = self.Model.construct(**data.dict())  # type: ignore

        if isinstance(data, dict):
            data = self.Model.construct(**data)

        self._data = data

    async def validate(self) -> bool:
        """
        Validate the form.

        :return: It will throw a ValidationError if the form is invalid
        """
        self.Model(**self.data())

        return True

    def on(self, event: OnEventLiteral, callback: OnCallbackEvent) -> None:
        """
        Add an event listener.

        :param event: The event to listen for
        :param callback: The callback function to call when the event is triggered

        Events:
            :submit:
                - Triggered when the form is submitted.
                - returns a boolean indicating if the form was successfully submitted.
        """
        if event not in self._on_events:
            self._on_events[event] = []

        self._on_events[event].append(callback)

    async def valid(self) -> bool:
        """
        Check if the form is valid.

        :return: True if the form is valid, False otherwise
        """
        try:
            self.Model(**self.data())
            return True
        except ValidationError:
            return False
