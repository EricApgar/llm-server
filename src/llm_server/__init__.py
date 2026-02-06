from typing import TYPE_CHECKING


__all__ = [
    'server'
]


def __getattr__(name: str):
    if name == 'server':
        from .server import Server
        return Server
    else:
        raise AttributeError(f'Module "llm_server" has no attribute {name!r}!')