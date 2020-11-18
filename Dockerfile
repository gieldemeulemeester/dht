FROM python:3.8

WORKDIR /user/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .
RUN chmod u+x ./*.py

HEALTHCHECK --interval=1m CMD python healthcheck.py
ENTRYPOINT [ "python", "am2302.py", "-L" ]
