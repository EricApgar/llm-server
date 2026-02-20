from __future__ import annotations

from abc import ABC
import weakref
from typing import TYPE_CHECKING
import base64
from io import BytesIO

import torch
from PIL import Image as PillowImage
import llm

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


    def add_model(self, tag: str, **kwargs):

        if tag in self.models:
            raise ValueError(f'Tage "{tag}" already in use by model.')
        
        self.models[tag] = llm.model(**kwargs)

        return
    

    def load_model(self, tag: str, **kwargs):

        if tag not in self.models:
            raise ValueError(f'No model with specified tag "{tag}"!')
        
        if 'device' not in kwargs:
            kwargs['device'] = self.get_device()

        self.models[tag].load(**kwargs)

        return
    

    def del_model(self, tag: str) -> None:

        if tag in self.models:
            del self.models[tag]

        return


    def list_models(self) -> list[str]:
        return {k: v.name for k, v in self.models.items()}
    

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

        response = Response(text=response)

        return response
    

    def ask(self, details: Request) -> str:

        input_args = details.model_dump()  # Convert to dict for later unpacking.
        del input_args['tag']  # Not a part of the input params for llm.ask().

        if input_args['images']:  # If using images input, assume model can handle images.
            input_args['images'] = [api_b64_to_PIL(i) for i in details.images]
        else:
            del input_args['images']
        
        response = self.models[details.tag].ask(**input_args)
        
        response = Response(text=response)

        return response
    

def api_b64_to_PIL(data_b64: str) -> PillowImage.Image:

    img_bytes = base64.b64decode(data_b64, validate=True)
    pil_image = PillowImage.open(BytesIO(img_bytes))
    pil_image.load()

    return pil_image
