FROM python:3.12

WORKDIR /sky_whale

COPY . .

RUN pip install -r requirements.txt

RUN ls -al

ENTRYPOINT ["python", "main.py"]
