from __future__ import annotations

import requests

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from llm_conversation import Conversation

from src.llm_server.helper.helper import encode_image


def ask(
    url: str,
    tag: str,
    prompt: str | Conversation,
    **kwargs) -> str:

    url += '/ask'

    if 'images' in kwargs:
        kwargs['images'] = [encode_image(i) for i in kwargs['images']]

    if not isinstance(prompt, str):  # If not string, assuming Conversation.
        prompt = prompt.to_dict()

    request_details = {
        'tag': tag,
        'prompt': prompt}
    
    request_details = request_details | kwargs

    try:
        response = requests.post(url, json=request_details)  # timeout=X.

        data = response.json()

    except Exception as e:
        raise(e)
    
    if 'text' not in data:
        raise ValueError(f'No "text" field in response: {response}')
    
    return data['text']


def ask_test(url: str) -> str:

    url += '/ask-test'

    try:
        response = requests.get(url)

        data = response.json()

    except Exception as e:
        raise(e)
    
    if 'text' not in data:
        raise ValueError(f'No "text" field in response: {response}')
    
    return data['text']


def get_models(url: str) -> dict:

    url += '/get-models'

    try:
        response = requests.get(url)

        data = response.json()

    except Exception as e:
        raise(e)
    
    return data