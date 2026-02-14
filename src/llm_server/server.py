from abc import ABC
import asyncio
import threading

import uvicorn

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
            asyncio.run(self._server.serve())
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

        self._PUBLIC_BACKEND = {
            'add_model',
            'del_model',
            'load_model',
            'list_models'}
        

    def __getattr__(self, name):
        '''
        Exposes a couple of backened methods directly to the user
        without them having to go through the backend.
        '''
        if name in self._PUBLIC_BACKEND:
            return getattr(self.backend, name)
        
        raise AttributeError(f'{type(self).__name__!s} has no attribute {name}!')


    def __dir__(self):

        return sorted(set(super().__dir__()) | self._PUBLIC_BACKEND)


if __name__ == '__main__':

    server = Server()
    server.set_host(ip_address='127.0.0.1', port=8000)
    server.add_model(tag='gpt', name='openai/gpt-oss-20b')
    server.load_model(tag='gpt', location=r'/home/eric/Repos/model_cache')
    server.start()

    import time
    time.sleep(100)  # llm-server is non-blocking.

    server.stop()

    pass