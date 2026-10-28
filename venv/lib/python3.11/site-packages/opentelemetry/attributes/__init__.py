# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

# pyright: reportUnnecessaryIsInstance=false

import copy
import logging
import threading
from collections.abc import Mapping, MutableMapping, Sequence
from types import NoneType
from typing import TYPE_CHECKING, Any, overload

from typing_extensions import assert_never, deprecated

from opentelemetry.util import types

_logger = logging.getLogger(__name__)


# Calling str(x) will use an object's `__str__` method if it exists, otherwise it will use it's `__repr__` method.
# If neither is defined it uses the base class's `object.__repr__` method, which returns a string that is hard to understand.
# So in that case we drop the key/value pair.
def _is_non_custom_str(key: Any) -> bool:
    return type(key).__str__ is not object.__str__ or type(key).__repr__ is not object.__repr__


@overload
def _clean_attribute_value(
    value: Mapping[str, types.AnyValue],
    max_string_value_length: int | None,
) -> Mapping[str, types.AnyValue]: ...


@overload
def _clean_attribute_value(
    value: types.AnyValue,
    max_string_value_length: int | None,
) -> types.AnyValue: ...


def _clean_attribute_value(
    value: types.AnyValue,
    max_string_value_length: int | None,
) -> types.AnyValue:
    """Recursively checks if an attribute value is valid and cleans it if required.

    String values are truncated to max_string_value_length if provided.
    Anything that isn't of `types.AnyValue`, we attempt to cast to `str`.
    If this fails, the value is replaced with None. Sequence's are converted to tuples and mappings
    are copied into new dicts.

    Returns:
        The recursively cleaned AnyValue.
    """
    if isinstance(value, (NoneType, bool, int, float, bytes)):
        return value
    if isinstance(value, str):
        if max_string_value_length is not None and len(value) > max_string_value_length:
            _logger.warning(
                "String attribute value exceeds max length of %d, truncating.",
                max_string_value_length,
            )
            value = value[:max_string_value_length]
        return value
    if isinstance(value, Sequence):
        return tuple(_clean_attribute_value(v, max_string_value_length) for v in value)
    if isinstance(value, Mapping):
        cleaned_mapping: dict[str, types.AnyValue] = {}
        for key, val in value.items():
            if not key:
                _logger.warning(
                    "invalid attribute key `%s`. must be non-empty string. Dropping key from attributes.",
                    key,
                )
                continue
            # Spec says to convert unknown types to strings if possible (here and below too).
            if not isinstance(key, str):
                _logger.warning(
                    "Invalid type `%s` for attribute key `%s`, must be a str. Key's `__str__/__repr__` method will be called if it exists, otherwise the key/value pair will be dropped.",
                    type(key),
                    key,
                )
                if _is_non_custom_str(key):
                    key = str(key)
                else:
                    continue
            cleaned_mapping[key] = _clean_attribute_value(val, max_string_value_length)
        return cleaned_mapping
    if TYPE_CHECKING:
        assert_never(value)
    _logger.warning(
        "Invalid type `%s` for attribute value. Expected one of bool, str, None, bytes, int, float or a "
        "Mapping or Sequence of those types. Value's __str__ method will be called if it exists, otherwise the value will be replaced with None.",
        type(value),
    )
    if _is_non_custom_str(value):
        return str(value)
    return None


class BoundedAttributes(MutableMapping[str, types.AnyValue]):
    """A dict with a fixed max capacity which cleans and potentially drops values to ensure they are valid attribute values.

    Args:
        maxlen: The maximum number of attributes to store, use None for no limit.
        attributes: The initial attributes to store.
        immutable: Defaults to true. Whether to allow adding/removing of attributes after the initialisation of the instance.
        max_value_len: The maximum length of string values, use None for no limit.
        extended_attributes: Deprecated. Kept for backwards compatibility. Extended attributes are now always used for attributes everywhere.

    When the dict is full and a new element is added, the oldest element is dropped. Attributes are made to be immutable when set in this container.
    So passing a mutable list as an attribute value, and then mutating it after will not change it's value in this container.
    """

    @overload
    def __init__(
        self,
        maxlen: int | None = None,
        attributes: types.Attributes = None,
        immutable: bool = True,
        max_value_len: int | None = None,
    ) -> None: ...

    @overload
    @deprecated(
        "Creating BoundedAttributes with `extended_attributes` set is deprecated. "
        "The `extended_attributes` param is no longer used and will be removed "
        "in a future release. Extended attributes are now always used for attributes everywhere."
    )
    def __init__(
        self,
        maxlen: int | None = None,
        attributes: types.Attributes = None,
        immutable: bool = True,
        max_value_len: int | None = None,
        extended_attributes: bool = False,
    ) -> None: ...

    def __init__(
        self,
        maxlen: int | None = None,
        attributes: types.Attributes = None,
        immutable: bool = True,
        max_value_len: int | None = None,
        extended_attributes: bool = False,
    ) -> None:
        if maxlen is not None and maxlen < 0:
            raise ValueError("maxlen must be valid int greater or equal to 0")
        if max_value_len is not None and max_value_len < 0:
            raise ValueError("max_value_len must be valid int greater or equal to 0")
        self._dict: dict[str, types.AnyValue] = {}
        self.maxlen = maxlen
        self.dropped = 0
        self.max_value_len = max_value_len
        self._lock = threading.Lock()
        # setting False before adding items
        self._immutable = False
        if attributes:
            self._set_items(attributes)
        self._immutable = immutable

    def __repr__(self) -> str:
        return f"{dict(self._dict)}"

    def __getitem__(self, key: str) -> types.AnyValue:
        return self._dict[key]

    def _raise_if_immutable(self) -> None:
        if self._immutable:
            raise TypeError("Cannot mutate immutable BoundedAttributes")

    def __setitem__(self, key: str, value: types.AnyValue) -> None:
        self._raise_if_immutable()
        if self.maxlen is not None and self.maxlen == 0:
            with self._lock:
                self.dropped += 1
                return
        if not key or not isinstance(key, str):
            _logger.warning(
                "invalid key `%s`. must be non-empty string. Dropping key from attributes.",
                key,
            )
            with self._lock:
                self.dropped += 1
            return
        cleaned = _clean_attribute_value(value, self.max_value_len)
        with self._lock:
            self._setitem_locked(key, cleaned)

    def _set_items(self, attributes: Mapping[str, types.AnyValue]) -> None:
        self._raise_if_immutable()
        if self.maxlen is not None and self.maxlen == 0:
            with self._lock:
                self.dropped += len(attributes)
            return
        cleaned_attributes: Mapping[str, types.AnyValue] = _clean_attribute_value(attributes, self.max_value_len)
        with self._lock:
            self.dropped += len(attributes) - len(cleaned_attributes)
            for key, value in cleaned_attributes.items():
                self._setitem_locked(key, value)

    def _setitem_locked(self, key: str, value: types.AnyValue) -> None:
        if key in self._dict:
            del self._dict[key]
        if self.maxlen is not None and len(self._dict) >= self.maxlen:
            _logger.warning(
                "Attributes dict is full. Dropping the oldest key-value pair from attributes to make space for the new key-value pair.",
            )
            # Dictionaries are insertion ordered in Python, this is the recommended way to get the oldest value.
            del self._dict[next(iter(self._dict.keys()))]
            self.dropped += 1

        self._dict[key] = value

    def __delitem__(self, key: str) -> None:
        self._raise_if_immutable()
        del self._dict[key]

    def __iter__(self):
        if self._immutable:
            return iter(self._dict)
        with self._lock:
            return iter(list(self._dict))

    def __len__(self) -> int:
        return len(self._dict)

    def __deepcopy__(self, memo: dict[int, Any]) -> "BoundedAttributes":
        copy_ = BoundedAttributes(
            maxlen=self.maxlen,
            immutable=self._immutable,
            max_value_len=self.max_value_len,
        )
        memo[id(self)] = copy_
        with self._lock:
            # Assign _dict directly to avoid re-cleaning already clean values
            # and to bypass the immutability guard in __setitem__
            copy_._dict = copy.deepcopy(self._dict, memo)
            copy_.dropped = self.dropped
        return copy_

    def copy(self) -> MutableMapping[str, types.AnyValue]:
        return self._dict.copy()
