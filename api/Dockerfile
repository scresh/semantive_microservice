FROM python

COPY . /api
WORKDIR /api

# install requirements
RUN pip install -r requirements.txt

# expose the app port
EXPOSE 5002

# run the app server
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "3", "app:app"]
