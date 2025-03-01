# Typing Extensions

[![Chat at https://gitter.im/python/typing](https://badges.gitter.im/python/typing.svg)](https://gitter.im/python/typing)

## Overview

The `typing_extensions` module serves two related purposes:

- Enable use of new type system features on older Python versions. For example,
  `typing.TypeGuard` is new in Python 3.10, but `typing_extensions` allows
  users on previous Python versions to use it too.
- Enable experimentation with new type system PEPs before they are accepted and
  added to the `typing` module.

New features may be added to `typing_extensions` as soon as they are specified
in a PEP that has been added to the [python/peps](https://github.com/python/peps)
repository. If the PEP is accepted, the feature will then be added to `typing`
for the next CPython release. No typing PEP has been rejected so far, so we
haven't yet figured out how to deal with that possibility.

Starting with version 4.0.0, `typing_extensions` uses
[Semantic Versioning](https://semver.org/). The
major version is incremented for all backwards-incompatible changes.
Therefore, it's safe to depend
on `typing_extensions` like this: `typing_extensions >=x.y, <(x+1)`,
where `x.y` is the first version that includes all features you need.

`typing_extensions` supports Python versions 3.7 and higher. In the future,
support for older Python versions will be dropped some time after that version
reaches end of life.

## Included items

This module currently contains the following:

- Experimental features

  - `override` (see [PEP 698](https://peps.python.org/pep-0698/))
  - The `default=` argument to `TypeVar`, `ParamSpec`, and `TypeVarTuple` (see [PEP 696](https://peps.python.org/pep-0696/))
  - The `infer_variance=` argument to `TypeVar` (see [PEP 695](https://peps.python.org/pep-0695/))
  - The `@deprecated` decorator (see [PEP 702](https://peps.python.org/pep-0702/))

- In `typing` since Python 3.11

  - `assert_never`
  - `assert_type`
  - `clear_overloads`
  - `@dataclass_transform()` (see [PEP 681](https://peps.python.org/pep-0681/))
  - `get_overloads`
  - `LiteralString` (see [PEP 675](https://peps.python.org/pep-0675/))
  - `Never`
  - `NotRequired` (see [PEP 655](https://peps.python.org/pep-0655/))
  - `reveal_type`
  - `Required` (see [PEP 655](https://peps.python.org/pep-0655/))
  - `Self` (see [PEP 673](https://peps.python.org/pep-0673/))
  - `TypeVarTuple` (see [PEP 646](https://peps.python.org/pep-0646/); the `typing_extensions` version supports the `default=` argument from [PEP 696](https://peps.python.org/pep-0696/))
  - `Unpack` (see [PEP 646](https://peps.python.org/pep-0646/))

- In `typing` since Python 3.10

  - `Concatenate` (see [PEP 612](https://peps.python.org/pep-0612/))
  - `ParamSpec` (see [PEP 612](https://peps.python.org/pep-0612/); the `typing_extensions` version supports the `default=` argument from [PEP 696](https://peps.python.org/pep-0696/))
  - `ParamSpecArgs` (see [PEP 612](https://peps.python.org/pep-0612/))
  - `ParamSpecKwargs` (see [PEP 612](https://peps.python.org/pep-0612/))
  - `TypeAlias` (see [PEP 613](https://peps.python.org/pep-0613/))
  - `TypeGuard` (see [PEP 647](https://peps.python.org/pep-0647/))
  - `is_typeddict`

- In `typing` since Python 3.9

  - `Annotated` (see [PEP 593](https://peps.python.org/pep-0593/))

- In `typing` since Python 3.8

  - `final` (see [PEP 591](https://peps.python.org/pep-0591/))
  - `Final` (see [PEP 591](https://peps.python.org/pep-0591/))
  - `Literal` (see [PEP 586](https://peps.python.org/pep-0586/))
  - `Protocol` (see [PEP 544](https://peps.python.org/pep-0544/))
  - `runtime_checkable` (see [PEP 544](https://peps.python.org/pep-0544/))
  - `TypedDict` (see [PEP 589](https://peps.python.org/pep-0589/))
  - `get_origin` (`typing_extensions` provides this function only in Python 3.7+)
  - `get_args` (`typing_extensions` provides this function only in Python 3.7+)

- In `typing` since Python 3.7

  - `OrderedDict`

- In `typing` since Python 3.5 or 3.6 (see [the typing documentation](https://docs.python.org/3.10/library/typing.html) for details)

  - `AsyncContextManager`
  - `AsyncGenerator`
  - `AsyncIterable`
  - `AsyncIterator`
  - `Awaitable`
  - `ChainMap`
  - `ClassVar` (see [PEP 526](https://peps.python.org/pep-0526/))
  - `ContextManager`
  - `Coroutine`
  - `Counter`
  - `DefaultDict`
  - `Deque`
  - `NewType`
  - `NoReturn`
  - `overload`
  - `Text`
  - `Type`
  - `TYPE_CHECKING`
  - `get_type_hints`

- The following have always been present in `typing`, but the `typing_extensions` versions provide
  additional features:

  - `Any` (supports inheritance since Python 3.11)
  - `NamedTuple` (supports multiple inheritance with `Generic` since Python 3.11)
  - `TypeVar` (see PEPs [695](https://peps.python.org/pep-0695/) and [696](https://peps.python.org/pep-0696/))

# Other Notes and Limitations

Certain objects were changed after they were added to `typing`, and
`typing_extensions` provides a backport even on newer Python versions:

- `TypedDict` does not store runtime information
  about which (if any) keys are non-required in Python 3.8, and does not
  honor the `total` keyword with old-style `TypedDict()` in Python
  3.9.0 and 3.9.1. `TypedDict` also does not support multiple inheritance
  with `typing.Generic` on Python <3.11.
- `get_origin` and `get_args` lack support for `Annotated` in
  Python 3.8 and lack support for `ParamSpecArgs` and `ParamSpecKwargs`
  in 3.9.
- `@final` was changed in Python 3.11 to set the `.__final__` attribute.
- `@overload` was changed in Python 3.11 to make function overloads
  introspectable at runtime. In order to access overloads with
  `typing_extensions.get_overloads()`, you must use
  `@typing_extensions.overload`.
- `NamedTuple` was changed in Python 3.11 to allow for multiple inheritance
  with `typing.Generic`.
- Since Python 3.11, it has been possible to inherit from `Any` at
  runtime. `typing_extensions.Any` also provides this capability.
- `TypeVar` gains two additional parameters, `default=` and `infer_variance=`,
  in the draft PEPs [695](https://peps.python.org/pep-0695/) and [696](https://peps.python.org/pep-0696/), which are being considered for inclusion
  in Python 3.12.

There are a few types whose interface was modified between different
versions of typing. For example, `typing.Sequence` was modified to
subclass `typing.Reversible` as of Python 3.5.3.

These changes are _not_ backported to prevent subtle compatibility
issues when mixing the differing implementations of modified classes.

Certain types have incorrect runtime behavior due to limitations of older
versions of the typing module:

- `ParamSpec` and `Concatenate` will not work with `get_args` and
  `get_origin`. Certain [PEP 612](https://peps.python.org/pep-0612/) special cases in user-defined
  `Generic`s are also not available.

These types are only guaranteed to work for static type checking.

## Running tests

To run tests, navigate into the appropriate source directory and run
`test_typing_extensions.py`.