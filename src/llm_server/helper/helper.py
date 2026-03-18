from io import BytesIO
import base64
from typing import Optional, overload

from PIL import Image as PillowImage


def encode_image(image: PillowImage.Image) -> str:
    """
    Encode a PIL image as a base64 string for API transport.
    """

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    encoded_output = base64.b64encode(buffer.getvalue()).decode('ascii')

    return encoded_output


class Endpoint:

    @overload
    def __init__(self, ip_address: str, port: int): ...

    @overload
    def __init__(self, string: str): ...

    def __init__(self,
        ip_address: Optional[str]=None,
        port: Optional[int]=None,
        string: Optional[str]=None):

        self.ip_address: str = ip_address
        self.port: int = port
        self.string: str = string

        self._parse()


    def _parse(self):

        if self.ip_address is not None and self.port is not None:
            self.string = f'{self.ip_address}:{self.port}'
        else:
            self.ip_address, port = self.string.split(':')
            self.port = int(port)

        return


    def __eq__(self, other) -> bool:

        if not isinstance(other, Endpoint):
            return NotImplemented

        return (self.ip_address, self.port) == (other.ip_address, other.port)
