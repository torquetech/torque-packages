FROM python:3.9

WORKDIR /task
CMD ["python", "-m", "task"]

COPY setup.py version.sh /task/
COPY requirements.txt /task/
COPY task /task/

RUN python -m pip install -r requirements.txt
RUN python -m pip install .
