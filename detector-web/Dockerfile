FROM python:3
RUN mkdir /python
WORKDIR /python
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt
ENTRYPOINT ["bash", "/python/run.sh"]
