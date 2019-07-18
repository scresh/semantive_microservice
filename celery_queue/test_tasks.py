from time import sleep

from celery import Celery
from celery.result import AsyncResult

celery_app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')


def test_get_url_text_html():
    url = 'https://pl.lipsum.com/'
    task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
    result = AsyncResult(task.task_id, app=celery_app).get()
    with open(result, 'r') as f:
        assert 'Lorem' in f.read()


def test_get_url_text_diacritic():
    url = 'https://pl.lipsum.com/'
    task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
    result = AsyncResult(task.task_id, app=celery_app).get()
    with open(result, 'r') as f:
        assert 'ą' in f.read()


def test_get_url_text_ssl_error():
    url = 'https://blank.org/'
    task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
    while task.status == 'PENDING':
        sleep(0.1)
    assert task.status == 'FAILURE'


def test_get_url_text_img():
    url = 'https://semantive.com/wp-content/uploads/2018/12/logo-white@0.5x.png'
    task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
    while task.status == 'PENDING':
        sleep(0.1)
    assert task.status == 'FAILURE'


def test_get_url_text_connection_err():
    url = 'http://thispagedoesntexist.com/'
    task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
    while task.status == 'PENDING':
        sleep(0.1)
    assert task.status == 'FAILURE'


def test_get_url_text_connection_timeout():
    url = 'http://www.google.com:81/'
    task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
    while task.status == 'PENDING':
        sleep(0.1)
    assert task.status == 'FAILURE'
