from __future__ import annotations

from abc import ABC
import weakref
from typing import TYPE_CHECKING
import base64
from io import BytesIO

import torch
from PIL import Image as PillowImage

from llm_server.schemas import Response

if TYPE_CHECKING:
    from llm_server.server import BaseServer, Server
    from llm_server.schemas import Request


class BaseBackend(ABC):

    def __init__(self, parent: BaseServer):
        
        self.parent = weakref.proxy(parent)


class Backend(BaseBackend):

    def __init__(self, parent: Server):
        super().__init__(parent=parent)

        self.models: dict = {}

    def get_model_list(self) -> list[str]:
        return list(self.models.keys())
    

    def get_device(self):

        all_device_count = torch.cuda.device_count()

        i = (len(self.models) - 1) % all_device_count

        device = f'gpu:{i}'

        return device
    

    def ask_test(self) -> str:

        first_key = next(iter(self.models), None)

        if first_key is None:
            return 'No models available.'
        
        response = self.models[first_key].ask(prompt='Tell me a joke.')

        return response
    

    def ask(self, details: Request) -> str:

        if details.images:
            images = [api_b64_to_PIL(i) for i in details.images]
        else:
            images = None

        response = self.parent.backend.models[details.tag].ask(
            prompt=details.prompt,
            images=images,
            max_tokens=details.max_tokens,
            temperature=details.temperature)
        
        response = Response(text=response)

        return response
    

def api_b64_to_PIL(data_b64: str) -> PillowImage.Image:

    img_bytes = base64.b64decode(data_b64, validate=True)
    pil_image = PillowImage.open(BytesIO(img_bytes))
    pil_image.load()

    return pil_image