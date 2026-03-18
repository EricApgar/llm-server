import json
import requests
from io import BytesIO
import base64

from PIL import Image as PillowImage
from llm_conversation import Conversation


def pil_to_api_b64(pil_image: PillowImage.Image) -> str:
	buffer = BytesIO()
	pil_image.save(buffer, format='PNG')

	return base64.b64encode(buffer.getvalue()).decode('ascii')


# TODO: Point to endpoint of hosted llm_server.Server().
URL = 'http://127.0.0.1:8001/ask'

# TODO: Edit as needed.
images = [pil_to_api_b64(PillowImage.open(r'/home/eric/Desktop/monkey.png'))]

# TODO: Edit as needed.
c = Conversation()
c.set_overall_prompt(text='Pretend to be a person named John Doe.')
c.add_context(text='Your favorite color is onyx.')
c.add_response(role='user', text='Whats your name and favorite color?')
prompt = c.to_dict()

# TODO: Edit as needed.
REQUEST_DETAILS = {
	'tag': 'Phi-4',
	'prompt': 'Describe the image.',
	'images': images}


def main() -> None:

	try:
		response = requests.post(URL, json=REQUEST_DETAILS, timeout=15)
		data = response.json()
		print(json.dumps(data, indent=4))

	except Exception as e:
		raise(e)

	return


if __name__ in {'__main__', '__mp_main__'}:

	# TODO: Make sure a server instance (llm_server.Server() or 
	# llm_server.server_gui()) is running before running main().
	main()
