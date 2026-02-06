from abc import ABC
import asyncio
import threading

import uvicorn
import llm

from llm_server.application import Application, BaseApplication
from llm_server.backend import Backend, BaseBackend
from llm_server.helper import Endpoint


class BaseServer(ABC):

    def __init__(self):

        self.application: BaseApplication = None  # In implementation, set to BaseApplication(parent=self).
        self.backend: BaseBackend = None  # In implementation, set to BaseBackend(parent=self).

        self.endpoint: Endpoint = None
        self.is_online: bool = False

        self.log: list = []

        self._server: uvicorn.Server = None
        self._thread: threading.Thread = None


    def set_host(self, ip_address: str, port: int) -> None:

        if self.is_online:
            raise ValueError('Cannot set host on active server. Must "stop()" first!')
            # TODO: Debating stopping, changing, and starting automatically here.

        self.endpoint = Endpoint(ip_address=ip_address, port=port)

        return
    

    def start(self):

        if self.is_online:
            return
        
        self.application._set_api()

        config = uvicorn.Config(
            app=self.application.api,
            host=self.endpoint.ip_address,
            port=self.endpoint.port)
            # TODO: loop='asyncio'

        self._server = uvicorn.Server(config=config)

        def run_server():
            asyncio.run(self._server.server())
            return

        self._thread = threading.Thread(target=run_server, daemon=True)
        self._thread.start()

        self.is_online = True

        return
    

    def stop(self):

        if self.is_online:
            self._server.should_exit = True
            self._thread.join()

            self.app = None
            self.is_online = False
            self._server = None
            self._thread = None

        return
    

class Server(BaseServer):

    def __init__(self):
        super().__init__()

        self.application: Application = Application(parent=self)
        self.backend: Backend = Backend(parent=self)


    def add_model(self, tag: str, **kwargs):

        if tag in self.backend.models:
            raise ValueError(f'Tage "{tag}" already in use by model.')
        
        self.backend.models[tag] = llm.model(**kwargs)

        return
    

    def load_model(self, tag: str, **kwargs):

        if tag not in self.backend.models:
            raise ValueError(f'No model with specified tag "{tag}"!')
        
        if 'device' not in kwargs:
            kwargs['device'] = self.backend.get_device()

        self.backend.models[tag].load(**kwargs)

        return
    

    def del_model(self, tag: str) -> None:

        if tag in self.backend.models:
            del self.backend.models[tag]

        return
    

if __name__ == '__main__':

    server = Server()
    server.set_host(ip_address='127.0.0.1', port=8000)
    server.add_model(tag='Phi-4', name='microsoft/Phi-4-multimodal-instruct')
    server.load_model(tag='Phi-4', location=r'<full path to model cache>')
    server.start()

    import time
    time.sleep(100)  # llm-server is non-blocking.

    server.stop()