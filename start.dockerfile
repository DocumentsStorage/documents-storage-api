FROM python:3.9-alpine3.13
LABEL maintainer="Daniel Goliszewski taafeenn@gmail.com"
LABEL version="0.8.4"
WORKDIR /usr/src/app/documents-storage-api

RUN apk add --no-cache musl-dev=1.2.2-r1 gcc=10.2.1_pre1-r3 libffi-dev=3.3-r2 git=2.30.3-r0
# Set user
RUN addgroup -S documents-storage && adduser -S documents-storage -G documents-storage
RUN chown documents-storage:documents-storage /usr/src/app/documents-storage-api
USER documents-storage

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["python", "documents_storage_api/main.py"]