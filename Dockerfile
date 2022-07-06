FROM python:3.8-slim

RUN apt-get update \
&& apt-get upgrade -y \
&& apt-get -y install libspatialindex-dev --no-install-recommends \
&& /usr/local/bin/python -m pip install --upgrade pip \
&& rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip3 install -e .

RUN groupadd -r arup && useradd --no-log-init -r -g arup arup

ENTRYPOINT ["mc"]
