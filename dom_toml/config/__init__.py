#!/usr/bin/env python3
#
#  __init__.py
"""
Nested configuration parsed from a TOML file.

.. extras-require:: config
	:pyproject:

.. versionadded:: 2.2.0
"""
#
#  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import json
from typing import Any, Dict, Mapping, Type, TypeVar

# 3rd party
import attrs  # nodep
import tomli_w  # nodep
from typing_extensions import Self  # nodep

# this package
import dom_toml

__all__ = ["Config", "ConfigMeta", "subtable_field"]

_C = TypeVar("_C", bound="Config")


def subtable_field(submethod_type: Type[_C]) -> _C:
	"""
	Attrs field for a nested table.

	:param submethod_type: The :class:`~.Config` for the table.
	"""

	def on_setattr(inst: object, attr: attrs.Attribute, value: Any) -> _C:
		return submethod_type._coerce(value)

	# Actually returns attr.Attribute, but mypy doesn't like it
	return attrs.field(factory=submethod_type, converter=submethod_type._coerce, on_setattr=on_setattr)


class ConfigMeta(type):
	"""
	Metaclass for :class:`~.Config`, which automatically decorates classes and subclasses with ``attrs.define``.
	"""

	def __new__(mcls, name, bases, ns):
		cls = super().__new__(mcls, name, bases, ns)
		if "__attrs_props__" in cls.__dict__:
			return cls
		else:
			return attrs.define(cls)


class Config(metaclass=ConfigMeta):
	"""
	Configuration parsed from a TOML file.
	"""

	@classmethod
	def from_dict(cls: Type[Self], config: Mapping[str, Any]) -> Self:
		"""
		Construct a :class:`~.Config` from a dictionary or TOML table.

		:param config:
		"""

		return cls(**config)

	def to_dict(self) -> Dict[str, Any]:
		"""
		Convert a :class:`~.Config` to a dictionary.
		"""

		return attrs.asdict(self, recurse=True)

	@classmethod
	def from_toml(cls: Type[Self], toml_string: str) -> Self:
		"""
		Parse a :class:`~.Config` from a TOML string.

		:param toml_string:
		"""

		parsed_toml = dom_toml.loads(toml_string)
		return cls(**parsed_toml["method"])

	@classmethod
	def from_json(cls: Type[Self], json_string: str) -> Self:
		"""
		Parse a :class:`~.Config` from a JSON string.

		:param json_string:
		"""

		parsed_json = json.loads(json_string)
		return cls(**parsed_json["method"])

	def to_toml(self) -> str:
		"""
		Convert a :class:`~.Config` to a TOML string.
		"""

		return tomli_w.dumps({"method": self.to_dict()})

	@classmethod
	def _coerce(cls: Type[Self], config: Any) -> Self:
		if isinstance(config, cls):
			return config
		elif isinstance(config, Mapping):
			return cls(**config)
		else:

			class_name = cls.__name__
			if class_name[0] in "aeiouAEIOU":
				raise TypeError(f"Cannot convert {type(config).__name__} to an {class_name}")
			# TODO: edge cases
			else:
				raise TypeError(f"Cannot convert {type(config).__name__} to a {class_name}")
