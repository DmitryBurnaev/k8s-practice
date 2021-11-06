FROM python:3.10-slim-buster
WORKDIR /app
RUN groupadd -r app && useradd -r -g app app
COPY src ./src
COPY etc/entrypoint.sh .
RUN chown -R app:app /app
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
