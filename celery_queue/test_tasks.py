from celery.result import AsyncResult
from celery import Celery
from time import sleep

celery_app = Celery('tasks', backend='redis://redis:6379', broker='redis://redis:6379')


class TestGetUrlText:
    def test_regular_html(self):
        url = 'https://pl.lipsum.com/'
        task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
        result = AsyncResult(task.task_id, app=celery_app).get()
        with open(result, 'r') as f:
            assert 'Lorem' in f.read()

    def test_html_with_diacritic(self):
        url = 'https://pl.lipsum.com/'
        task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
        result = AsyncResult(task.task_id, app=celery_app).get()
        with open(result, 'r') as f:
            assert 'ą' in f.read()

    def test_site_with_ssl_error(self):
        url = 'https://blank.org/'
        task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
        while task.status == 'PENDING':
            sleep(0.1)
        assert task.status == 'FAILURE'

    def test_non_html_page(self):
        url = 'https://semantive.com/wp-content/uploads/2018/12/logo-white@0.5x.png'
        task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
        while task.status == 'PENDING':
            sleep(0.1)
        assert task.status == 'FAILURE'

    def test_non_existing_page(self):
        url = 'http://thispagedoesntexist.com/'
        task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
        while task.status == 'PENDING':
            sleep(0.1)
        assert task.status == 'FAILURE'

    def test_timeout(self):
        url = 'http://www.google.com:81/'
        task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
        while task.status == 'PENDING':
            sleep(0.1)
        assert task.status == 'FAILURE'


class TestGetUrlImages:
    def test_many_images(self):
        url = 'http://www.softicons.com/social-media-icons/extreme-folded-social-icons-by-uiconstock'
        task = celery_app.send_task('tasks.get_url_images', args=[url], kwargs={})
        while task.status == 'PENDING':
            sleep(0.1)
        assert task.status == 'SUCCESS'

    def test_big_image(self):
        url = 'https://heapershangout.com/index.php?p=/discussion/5542/images-that-are-too-big-image-heavy'
        task = celery_app.send_task('tasks.get_url_images', args=[url], kwargs={})
        while task.status == 'PENDING':
            sleep(0.1)
        assert task.status == 'SUCCESS'

