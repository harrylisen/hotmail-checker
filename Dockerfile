FROM python:3.12.3-slim

WORKDIR /hotmail-checker
COPY . /hotmail-checker
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

CMD ["python", "hotmail-checker/main.py"]
