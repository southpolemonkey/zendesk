FROM python:3.8

COPY . /work
WORKDIR /work

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app.py"]

