"""
Module provides decorators for creating UI elements and actions in Python.

The ui_element decorator is used for creating UI elements and grouping them under a specified group.
The ui_action decorator is used for defining actions on UI elements and allows for updating their properties.
"""
from __future__ import annotations

import inspect

# https://docs.python.org/3/library/functools.html#functools.wraps
# wraps is used to alow for conditional args and kwargs and to preserve the original function name and docstring
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, Optional, TypeVar

if TYPE_CHECKING:
    from .base_form import BaseForm

from nicegui import ui
from nicegui.globals import asyncio

from .base_form import FormError

UiTypes = ui.element | ui.input | ui.button

RT = TypeVar("RT")

# We know that the private methods are being used in the BaseForm class, and these
# decorators are only used in the BaseForm class
# pyright: reportPrivateUsage=false


def _ui_wrapper(
    func: Any,
    self: Any,
    group: Optional[str],
    callback: Callable[[UiTypes, Any], Optional[UiTypes]] = lambda element: element,  # type: ignore
    *args,  # type: ignore
    **kwargs,  # type: ignore
) -> Any:
    func_name = f"_{func.__name__}"

    if not hasattr(self, func_name):
        el = func(self, *args, **kwargs)

        if len(inspect.signature(callback).parameters) == 2:
            callback(el, self)  # type: ignore
        else:
            callback(el)  # type: ignore

        if not hasattr(self, "_ui_groups"):
            self._ui_groups = {}

        if group not in self._ui_groups:
            self._ui_groups[group] = []

        setattr(self, func_name, el)

    element = getattr(self, func_name)

    self._ui_groups[group].append(element)  # type: ignore

    return element


def ui_element(*, group: Optional[str] = None) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """
    ui_element decorator.

    :param group: The group name to which the UI element belongs. Defaults to None
    """

    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        @wraps(func)
        def wrapper(self: Any, *args, **kwargs) -> RT:  # type: ignore
            return _ui_wrapper(func, self, *args, group=group, **kwargs)

        return wrapper  # type: ignore

    return decorator


async def _ui_input_valid(name: str, element: ui.input, form: BaseForm[Any], silent: bool = False) -> bool:
    if not hasattr(form, "Model"):
        return True

    if not hasattr(form.Model, f"validate_{name}"):
        return True

    validator = getattr(form.Model, f"validate_{name}")

    no_errors = True

    # Rescue the pydantic validation error and display it in the UI
    try:
        # check to see if it's a coroutine
        if inspect.iscoroutinefunction(validator):
            await validator(element.value)
        else:
            validator(element.value)
    except ValueError as e:
        no_errors = False
        if not silent:
            element.props(f'error error-message="{str(e)}"')

    return no_errors


async def _trigger_submit(form: BaseForm[Any]) -> Any:
    errors = []
    first_error_element = None

    for input_element in form._ui_inputs:
        # check using isinstance to see if awaitable
        valid = await _ui_input_valid(input_element.__ui_name__, input_element, form)  # type: ignore
        errors.append(valid)
        # focus on the first input with an error, only focus on the first
        if not first_error_element and not valid:
            first_error_element = input_element

    # if no errors, trigger the action which might be on form
    if all(errors) and hasattr(form, "_ui_submit_trigger"):
        form._form_valid = True
        await form._ui_submit_trigger()
        form._form_valid = False

    return first_error_element


# NOTE: This is a hack to handle async and none async validation functions
def _ui_input_valid_callback(name: str, element: ui.input, form: BaseForm[Any]) -> None:
    async def inner_async_function():
        asyncio.create_task(_ui_input_valid(name, element, form))

    loop = asyncio.get_event_loop()

    if loop.is_running():
        loop.create_task(inner_async_function())
    else:
        loop.run_until_complete(inner_async_function())


def _ui_input_callback(name: str, element: UiTypes, form: BaseForm[Any]) -> Any:
    if not isinstance(element, ui.input):
        return element

    # NOTE: This is a hack to get the name of the input
    element.__ui_name__ = name  # type: ignore

    form._ui_inputs.append(element)

    if hasattr(form._data, name):
        element.bind_value(form._data, name)

    async def _on_enter() -> None:
        # NOTE: This is a hack is to make sure we have the most up to date value, due to the debounce
        await ui.run_javascript(f"return getElement({element.id}).getNativeElement()")
        await _trigger_submit(form)
        element.run_method("focus")

    # NOTE: Debounce helps with server performance
    element.props("debounce=500")
    element.on("keydown.enter", _on_enter)
    element.on("blur", lambda: _ui_input_valid_callback(name, element, form))


def ui_input(
    *,
    name: str,
    group: Optional[str] = None,
) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """ui_input decorator."""

    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        @wraps(func)
        def wrapper(self: Any, *args, **kwargs) -> RT:  # type: ignore
            return _ui_wrapper(
                func,
                self,
                *args,
                group=group,
                callback=lambda element, form: _ui_input_callback(name, element, form),
                **kwargs,
            )

        return wrapper  # type: ignore

    return decorator


def _ui_submit_callback(element: UiTypes, form: BaseForm[Any]) -> Any:
    async def _on_submit() -> None:
        first_error_element = await _trigger_submit(form)

        if first_error_element:
            first_error_element.run_method("focus")

    element.props("type=submit")
    element.on("click", _on_submit)


def ui_submit(
    *,
    group: Optional[str] = None,
    trigger: str,
) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """ui_submit decorator."""

    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        @wraps(func)
        def wrapper(self: Any, *args, **kwargs) -> RT:  # type: ignore
            # Save the _ui_submit_trigger to the form and throw an error if it already exists
            # you can only have one submit button form
            if hasattr(self, "_ui_submit_trigger"):
                raise FormError("You can only have one submit button per form")
            else:
                self._ui_submit_trigger = getattr(self, trigger)

            self._ui_submit = _ui_wrapper(
                func,
                self,
                *args,
                group=group,
                callback=lambda element, form: _ui_submit_callback(element, form),
                **kwargs,
            )

        return wrapper  # type: ignore

    return decorator


def ui_action(
    *, props: Dict[str, Any]
) -> Callable[[Callable[..., Coroutine[RT, RT, RT]]], Callable[..., Coroutine[RT, RT, RT]]]:
    """
    ui_action decorator.

    :param props: A dictionary of properties to be updated before and after the action is executed.
    """

    def decorator(func: Callable[..., Coroutine[RT, RT, RT]]) -> Callable[..., Coroutine[RT, RT, RT]]:
        @wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> RT:
            async def update_props(action: Any) -> None:
                for key, value in props.items():
                    target_elements = [value] if isinstance(value, str) else value

                    for element in target_elements:
                        if isinstance(element, str):
                            if element.startswith("group="):
                                group = value[6:]
                                if hasattr(self, "_ui_groups") and group in self._ui_groups:
                                    target_elements.extend(self._ui_groups[group])
                                continue

                            element = getattr(self, f"_{element}")

                        element.props(**{action: key})

            await update_props("add")
            result = await func(self, *args, **kwargs)
            await update_props("remove")

            return result

        return wrapper

    return decorator


def submit() -> Callable[[Callable[..., Coroutine[bool, bool, bool]]], Callable[..., Coroutine[bool, bool, bool]]]:
    """
    Wrap an asynchronous function representing a submit action.

    This will stop validation being triggered if the form is already valid, which happens with ui submits,
    as the ui already validated the form.
    """

    def decorator(func: Callable[..., Coroutine[bool, bool, bool]]) -> Callable[..., Coroutine[bool, bool, bool]]:
        @wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> bool:
            valid = False
            valid_response = None

            if not self._form_valid:
                valid_response = await self.validate()
                valid = False if valid_response is None else valid_response

            if valid_response is None or valid:
                valid = await func(self, *args, **kwargs)

                if events := self._on_events["submit"]:
                    # loop through all the events and run them
                    for event in events:
                        # check if the event is a coroutine or normal function
                        if asyncio.iscoroutinefunction(event):
                            await event(valid)
                        else:
                            event(valid)

            return valid

        return wrapper

    return decorator
