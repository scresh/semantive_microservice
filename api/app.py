from flask_restful import Resource, Api, reqparse
from celery import Celery
from flask import Flask

PORT = 5002

app = Flask(__name__)
api = Api(app)
celery_app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')


class TextResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.url_param = 'url'
        self.parser.add_argument(self.url_param)

    def post(self):
        url = self.parser.parse_args().get(self.url_param)
        if url:

            task = celery_app.send_task('tasks.get_url_text', args=[url], kwargs={})
            return {'Response': 'OK',
                    'Message': f'Task ID: {task.task_id}'}
        else:
            return {'Response': 'ERROR',
                    'Message': 'Incorrect param'}


class ImageResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.url_param = 'url'
        self.parser.add_argument(self.url_param)

    def post(self):
        return self.parser.parse_args()


class TaskResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.task_param = 'task_id'
        self.parser.add_argument(self.task_param)

    def get(self):
        return self.parser.parse_args()


class DownloadResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.task_param = 'task_id'
        self.parser.add_argument(self.task_param)

    def get(self):
        return self.parser.parse_args()


api.add_resource(TextResource, '/text')
api.add_resource(ImageResource, '/image')
api.add_resource(TaskResource, '/task')
api.add_resource(DownloadResource, '/download')


if __name__ == '__main__':
    app.run(port=str(PORT))
