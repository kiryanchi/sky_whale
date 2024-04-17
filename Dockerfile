FROM python:3.12

WORKDIR /sky_whale

COPY ./sky_whale ./sky_whale
COPY ./main.py ./main.py
COPY ./requirements.txt ./requirements.txt
COPY ./setting.py ./setting.py

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
