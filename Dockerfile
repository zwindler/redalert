FROM python:3.8-slim-buster

RUN pip3 install flask slackclient && groupadd -r flask && \
    useradd -d /home/flask --no-log-init --create-home -r -g flask flask

COPY *.py /home/flask/

USER flask

WORKDIR /home/flask/

EXPOSE 3000

ENTRYPOINT ["python3", "redalert.py"]
