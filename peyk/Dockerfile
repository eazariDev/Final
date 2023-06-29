FROM python:3.11.4-slim

COPY requirements.txt .

RUN pip install \
    -i http://mirrors.aliyun.com/pypi/simple \
    --trusted-host mirrors.aliyun.com \
    -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "80"]
