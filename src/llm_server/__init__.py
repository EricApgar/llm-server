from typing import TYPE_CHECKING


__all__ = [
    'Server'
]


def __getattr__(name: str):
    if name == 'Server':
        from .server import Server
        return Server
    else:
        raise AttributeError(f'Module "llm_server" has no attribute {name!r}!')