from zipfile import ZipFile
from app import HOST, PORT
from io import BytesIO
from time import sleep
from PIL import Image
import requests


class TestTextDownload:
    def test_invalid_param(self):
        response = requests.post(f'http://{HOST}:{PORT}/text', data={'URL': 'http://example.com/'})
        assert response.json().get('Response') == 'ERROR'

    def test_filename(self):
        response = requests.post(f'http://{HOST}:{PORT}/text', data={'url': 'http://example.com/'})
        assert response.json().get('Response') == 'OK'
        task_url = response.json().get('Message')
        task_id = task_url[-36:]

        while requests.get(task_url).json().get('Response') == 'PENDING':
            sleep(0.1)

        download_url = requests.get(task_url).json().get('Message')

        download_response = requests.get(download_url)
        assert f'{task_id}.txt' in download_response.headers['content-disposition']


class TestImagesDownload:
    def test_zip_crf_and_headers(self):
        response = requests.post(f'http://{HOST}:{PORT}/images', data={'url': 'https://semantive.com/'})
        assert response.json().get('Response') == 'OK'
        task_url = response.json().get('Message')

        while requests.get(task_url).json().get('Response') == 'PENDING':
            sleep(0.1)

        download_url = requests.get(task_url).json().get('Message')

        download_response = requests.get(download_url).content

        with ZipFile(BytesIO(download_response), 'r') as zip_object:
            assert zip_object.testzip() is None

    def test_animated_gif(self):
        response = requests.post(f'http://{HOST}:{PORT}/images', data={'url': 'https://www.kedifilm.com/about'})
        task_url = response.json().get('Message')

        while requests.get(task_url).json().get('Response') == 'PENDING':
            sleep(0.1)

        download_url = requests.get(task_url).json().get('Message')
        download_response = requests.get(download_url).content

        with ZipFile(BytesIO(download_response), 'r') as zip_object:
            first_gif_name = [file for file in zip_object.namelist() if file.endswith('.gif')][0]
            first_gif = Image.open(BytesIO(zip_object.read(first_gif_name)))
            assert first_gif.seek(1) is None


