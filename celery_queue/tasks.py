from celery.exceptions import Ignore
from celery import Celery, states
from bs4 import BeautifulSoup
import requests
import tempfile

TIMEOUT = 5
FORBIDDEN_TAGS = ["script", "style", "table", "a", "img", "button", "header", "footer", "nav"]

celery_app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')


@celery_app.task(bind=True)
def get_url_text(self, url):
    try:
        response = requests.get(url, timeout=TIMEOUT)
        html = response.text

        soup = BeautifulSoup(html, features="html.parser")

        if not soup.find('html'):
            raise TypeError

        for tag in soup.findAll(FORBIDDEN_TAGS):
            tag.extract()

        text = ' '.join(soup.get_text().split())

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        temp_file.write(str.encode(text))
        temp_file.close()

        return temp_file.name

    except Exception as e:
        raise TaskFailure(self, e)


class TaskFailure(Exception):
    def __init__(self, task, exception):
        task.update_state(
            state=states.FAILURE,
            meta={
                'exc_message': (type(exception).__name__,),
                'custom': '', 'exc_type': '',
            })
        raise Ignore()
