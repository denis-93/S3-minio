FROM python

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /S3Project

COPY requirements.txt .
COPY entrypoint.sh .

EXPOSE 8000

RUN pip install -r requirements.txt
RUN chmod +x entrypoint.sh

COPY . .

ENTRYPOINT ["/S3Project/entrypoint.sh"]