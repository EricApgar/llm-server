import json
import requests
from io import BytesIO
import base64

from PIL import Image as PillowImage
from llm_conversation import Conversation

from llm_server.gui_app import run_gui


def pil_to_api_b64(pil_image: PillowImage.Image) -> str:
  buffer = BytesIO()
  pil_image.save(buffer, format='PNG')

  return base64.b64encode(buffer.getvalue()).decode('ascii')


URL = 'https://127.0.0.1:8000/ask'

# images = [pil_to_api_b64(PillowImage.open('<path to image>'))]

c = Conversation()
c.set_overall_prompt(text='Pretend to be a person named John Doe.')
c.add_context(text='Your favorite color is onyx.')
c.add_response(role='user', text='Whats your name and favorite color?')
prompt = c.to_dict()

REQUEST_DETAILS = {
	'tag': 'GPT',
	'prompt': prompt, #'Name a primary color.',
	# 'images': images,
	'max_tokens': 64,
	'temperature': 0.9,}


def main() -> None:

	try:
		response = requests.post(URL, json=REQUEST_DETAILS, timeout=15)
		data = response.json()
		print(json.dumps(data, indent=4))

	except Exception as e:
		raise(e)

	return


if __name__ in {'__main__', '__mp_main__'}:

	run_gui()

	# main()
