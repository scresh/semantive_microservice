FROM python

COPY . /celery_queue
WORKDIR /celery_queue

# install requirements
RUN pip install -r requirements.txt

# run the app server
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
