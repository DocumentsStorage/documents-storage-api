FROM python:3.9-alpine3.13
LABEL maintainer="Daniel Goliszewski taafeenn@gmail.com"
LABEL version="0.8.4"
WORKDIR /usr/src/app/documents-storage-api
# Set user
RUN groupadd -r documents-storage && useradd --no-log-init -r -g documents-storage documents-storage
USER documents-storage
COPY . .
RUN apk add --no-cache musl-dev=1.2.2-r1 gcc=10.2.1_pre1-r3 libffi-dev=3.3-r2 git=2.30.3-r0
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["python", "documents_storage_api/main.py"]