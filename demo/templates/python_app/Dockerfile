FROM python:3.9

WORKDIR /app
CMD ["python", "-m", "app"]

COPY setup.py version.sh /app/
COPY requirements.txt /app/
COPY app /app/

RUN python -m pip install -r requirements.txt
RUN python -m pip install .
