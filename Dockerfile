FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY ./example /code/example
COPY ./pages /code/pages
COPY requirements-frozen.txt /code/
RUN pip install -r requirements-frozen.txt