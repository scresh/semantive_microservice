from app import HOST, PORT
from time import sleep
import requests


def test_text_download_invalid_param():
    response = requests.post(f'http://{HOST}:{PORT}/text', data={'URL': 'http://example.com/'})
    assert response.json().get('Response') == 'ERROR'


def test_text_download_filename():
    response = requests.post(f'http://{HOST}:{PORT}/text', data={'url': 'http://example.com/'})
    assert response.json().get('Response') == 'OK'
    task_url = response.json().get('Message')
    task_id = task_url[-36:]

    while requests.get(task_url).json().get('Response') == 'PENDING':
        sleep(0.1)

    download_url = requests.get(task_url).json().get('Message')

    download_response = requests.get(download_url)
    assert f'{task_id}.txt' in download_response.headers['content-disposition']
