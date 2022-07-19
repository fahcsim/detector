FROM ubuntu
RUN mkdir /python
WORKDIR /python
COPY requirements.txt /tmp/requirements.txt
RUN apt update && apt install python3-pip -y && python3 -m pip install -r /tmp/requirements.txt
ENTRYPOINT ["bash", "/python/run.sh"]
