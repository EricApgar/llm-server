"""
Tests for llm_server.Server.

These tests can load a real model when hosting the server, so if running a full
test they require local model weights. Sync the environment first, then pass
LLM_MODEL_CACHE inline when invoking pytest so it only exists for that one
command and does not persist in your shell:

    uv sync --extra dev
    LLM_MODEL_CACHE=<path to model cache dir> pytest

Tests are skipped automatically if LLM_MODEL_CACHE is not set.

Make sure the virtual environment is active.
"""

import os
import time

import pytest
import requests
from PIL import Image as PillowImage

import llm_server
from llm_server.helper.helper import encode_image


MODEL_CACHE = os.environ.get('LLM_MODEL_CACHE')


@pytest.fixture(scope='module')
def server():
    s = llm_server.Server()
    s.set_host(ip_address='127.0.0.1', port=8001)
    s.start()
    time.sleep(1)  # Allow uvicorn to finish starting.
    yield s
    s.stop()


@pytest.fixture(scope='function')
def server_with_model():
    if not MODEL_CACHE:
        pytest.skip('LLM_MODEL_CACHE environment variable not set.')
    s = llm_server.Server()
    s.set_host(ip_address='127.0.0.1', port=8002)
    s.add_model(tag='gpt', name='openai/gpt-oss-20b')
    s.load_model(tag='gpt', location=MODEL_CACHE)
    s.start()
    time.sleep(1)  # Allow uvicorn to finish starting.
    yield s
    s.del_model(tag='gpt')  # Free GPU memory before teardown.
    s.stop()


def test_server_running(server):
    response = requests.get('http://127.0.0.1:8001/', timeout=5)
    assert response.json() == 'Running.'


def test_ask(server_with_model):
    response = requests.post(
        'http://127.0.0.1:8002/ask',
        json={'tag': 'gpt', 'prompt': 'Name a primary color.'},
        timeout=60)
    data = response.json()
    assert isinstance(data['text'], str)
    assert len(data['text']) > 0


@pytest.fixture(scope='module')
def server_with_multimodal_model():
    if not MODEL_CACHE:
        pytest.skip('LLM_MODEL_CACHE environment variable not set.')
    s = llm_server.Server()
    s.set_host(ip_address='127.0.0.1', port=8003)
    s.add_model(tag='phi4', name='microsoft/Phi-4-multimodal-instruct')
    s.load_model(tag='phi4', location=MODEL_CACHE)
    s.start()
    time.sleep(1)  # Allow uvicorn to finish starting.
    yield s
    s.stop()


@pytest.fixture(scope='module')
def red_square_image():
    return PillowImage.new('RGB', (64, 64), color=(255, 0, 0))


def test_ask_with_image(server_with_multimodal_model, red_square_image):
    response = requests.post(
        'http://127.0.0.1:8003/ask',
        json={
            'tag': 'phi4',
            'prompt': 'Describe the image.',
            'images': [encode_image(red_square_image)],
        },
        timeout=60)
    data = response.json()
    assert isinstance(data['text'], str)
    assert len(data['text']) > 0
