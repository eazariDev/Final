FROM python:3.11.4-slim

COPY requirements.txt .

RUN pip install \
    -i http://mirrors.aliyun.com/pypi/simple \
    --trusted-host mirrors.aliyun.com \
    -r requirements.txt

COPY main.py .

ENTRYPOINT [ "python", "main.py" ]
