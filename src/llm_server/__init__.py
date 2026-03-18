from __future__ import annotations
from typing import TYPE_CHECKING, Any


__all__ = [
    'Server',
    'server_gui',
]


if TYPE_CHECKING:
    from .server import Server
    from .gui_app import run_gui as server_gui


def __getattr__(name: str):
    if name == 'Server':
        from .server import Server
        globals()[name] = Server
        return Server
    elif name == 'server_gui':
        from .gui_app import run_gui as server_gui
        globals()[name] = server_gui
        return server_gui
    else:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(__all__))