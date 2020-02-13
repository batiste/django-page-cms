FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY ./pages /code/pages
COPY ./example /code/example
COPY requirements-frozen.txt /code/
RUN pip install -r requirements-frozen.txt