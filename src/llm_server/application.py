from __future__ import annotations

from abc import ABC, abstractmethod
import weakref
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from llm_server.schemas import Request, Response

if TYPE_CHECKING:
    from llm_server.server import BaseServer, Server


class BaseApplication(ABC):
    def __init__(self, parent: BaseServer):
        
        self.parent = weakref.proxy(parent)

        self.api: FastAPI = None


    @abstractmethod
    def _set_api(self):

        self.api = FastAPI()


        @self.api.get('/')
        def default() -> str:

            return 'Running.'
        

class Application(BaseApplication):

    def __init__(self, parent: Server):
        super().__init__(parent=parent)


    def _set_api(self):

        self.api = FastAPI()


        @self.api.get('/')
        def default() -> str:

            return 'Running.'
        

        @self.api.get('/get-models')
        def get_models() -> dict:

            model_list = self.parent.backend.list_models()

            return model_list
        

        @self.api.get('/ask-test', response_class=PlainTextResponse)
        async def ask_test() -> str:
            
            response = self.parent.backend.ask_test()

            return response
        

        @self.api.post('/ask', response_model=Response)
        async def ask(details: Request) -> Response:

            try:
                response = self.parent.backend.ask(details=details)

                return response
            
            except KeyError:
                raise HTTPException(status_code=404, detail=f'Unknown model tag: {details.tag}')
            except RuntimeError as e:
                raise HTTPException(status_code=409, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            
        return