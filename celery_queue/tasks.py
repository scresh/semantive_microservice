import imghdr
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from celery.exceptions import Ignore
from celery import Celery, states
from bs4 import BeautifulSoup
import requests

TIMEOUT = 5
FORBIDDEN_TAGS = ["script", "style", "table", "a", "img", "button", "header", "footer", "nav"]

celery_app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')


@celery_app.task(bind=True)
def get_url_text(self, url):
    try:
        html = requests.get(url, timeout=TIMEOUT).text
        soup = BeautifulSoup(html, features="html.parser")

        if not soup.find('html'):
            raise TypeError

        for tag in soup.findAll(FORBIDDEN_TAGS):
            tag.extract()

        text = ' '.join(soup.get_text().split())
        text_file = NamedTemporaryFile(delete=False, suffix='.txt')
        text_file.write(str.encode(text))
        text_file.close()

        return text_file.name

    except Exception as e:
        raise TaskFailure(self, e)


@celery_app.task(bind=True)
def get_url_images(self, url):
    try:
        html = requests.get(url, timeout=TIMEOUT).text
        urls = get_url_img_hrefs(html, url)

        zip_file = NamedTemporaryFile(delete=False, suffix='.zip')
        with ZipFile(zip_file.name, 'w') as zip_object:
            for i, url in enumerate(urls):
                img_bytes = requests.get(url, stream=True).content
                add_image_to_zip_object(img_bytes, i, zip_object)

        return zip_file.name

    except Exception as e:
        raise TaskFailure(self, e)


def get_url_img_hrefs(html, url):
    soup = BeautifulSoup(html, features="html.parser")

    img_urls = [tag.get('src') for tag in soup.findAll('img', src=True)]
    domain = get_url_domain(url)
    return fix_relative_urls(img_urls, domain)


def get_url_domain(url):
    return '/'.join(url.split('/')[:3])


def fix_relative_urls(urls, domain):
    return [*map(lambda url: domain + url if url[0] == '/' else url, urls)]


def add_image_to_zip_object(img_bytes, filename, zip_object,):
    with NamedTemporaryFile() as img_file:
        img_file.write(img_bytes)
        img_type = imghdr.what(img_file.name)
        if img_type:
            zip_object.write(img_file.name, f'{filename}.{img_type}')


class TaskFailure(Exception):
    def __init__(self, task, exception):
        task.update_state(
            state=states.FAILURE,
            meta={
                'exc_message': (type(exception).__name__, ),
                'custom': '', 'exc_type': '',
            })
        raise Ignore()
