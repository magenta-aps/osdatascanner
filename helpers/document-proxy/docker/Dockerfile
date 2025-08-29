FROM python:3.13.6-bookworm AS application

ENV PYTHONUNBUFFERED=1 \
  PYTHONPATH=/code/src/:$PYTHONPATH

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /code/docker
COPY docker .

WORKDIR /code/src
COPY src .

WORKDIR /code/requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER nobody:nogroup

# Just for debugging:
RUN find /code -type f -print0 | xargs -0 -- ls -al

EXPOSE 5000
ENTRYPOINT ["/code/docker/docker-entrypoint.sh"]
CMD ["gunicorn", "--config", "/code/docker/gunicorn-settings.py", "document_proxy:app"]
