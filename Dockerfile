FROM thinkwhere/gdal-python:3.7-ubuntu

COPY . .
RUN pip3 install -r requirements.txt
RUN pip3 install -e .

ENTRYPOINT ["mc"]
