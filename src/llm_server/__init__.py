from __future__ import annotations
from typing import TYPE_CHECKING


__all__ = [
    'Server',
    'run_gui',
    'encode_image',
]


if TYPE_CHECKING:
    from .server import Server
    from .gui_app import run_gui as run_gui
    from .helper.helper import encode_image


def __getattr__(name: str):
    if name == 'Server':
        from .server import Server
        globals()[name] = Server
        return Server
    elif name == 'run_gui':
        from .gui_app import run_gui
        globals()[name] = run_gui
        return run_gui
    elif name == 'encode_image':
        from .helper.helper import encode_image
        globals()[name] = encode_image
        return encode_image
    else:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(__all__))