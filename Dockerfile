FROM python:3.8-slim-buster
ENV FLASK_RUN_HOST=0.0.0.0
WORKDIR /flashlearn

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

RUN chmod u+x ./entrypoint.sh

CMD ["./entrypoint.sh"]
