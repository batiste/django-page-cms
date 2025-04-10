FROM python:3.12-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY ./example /code/example
COPY ./pages /code/pages
COPY ./doc /code/doc
COPY README.rst /code/
COPY requirements-frozen.txt /code/
COPY setup.py /code/
RUN pip install .[full]