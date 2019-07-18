from flask import Flask
from flask_restful import Resource, Api, reqparse


app = Flask(__name__)
api = Api(app)


class TextResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.url_param = 'url'
        self.parser.add_argument(self.url_param)

    def post(self):
        return self.parser.parse_args()


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
    app.run(port='5002')    # TODO: Move to config file
