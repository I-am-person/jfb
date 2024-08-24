FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install Flask

RUN apt-get update && \
    apt-get install -y wget && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/github/codeql-action/releases/download/codeql-bundle-v2.17.5/codeql-bundle-linux64.tar.gz && \
    tar -xzf codeql-bundle-linux64.tar.gz -C /opt && \
    rm codeql-bundle-linux64.tar.gz

ENV PATH="/opt/codeql/:/usr/src/app:${PATH}"

RUN mkdir -p /opt/db/0 && mkdir /opt/db/1

RUN python shuffler.py /opt/db/0 && python shuffler.py /opt/db/1

CMD ["python", "app.py"]
