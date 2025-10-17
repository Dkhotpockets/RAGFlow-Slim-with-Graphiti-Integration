# Ragflow Slim Dockerfile
# Contributor-safe, production-ready containerization

FROM python:3.11.8-alpine3.19


# NOTE: Ensure all dependencies in requirements.txt are pinned to specific versions and include hashes for security.


# Install build tools and poppler-utils for Alpine
RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache build-base poppler-utils

WORKDIR /app

COPY . /app

RUN python -m venv .venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install --require-hashes -r requirements.txt


# Expose Flask port
EXPOSE 5000

# Create outputs folder for contributor safety
RUN mkdir -p /app/outputs

RUN adduser -D -h /home/ragflowuser -s /bin/sh ragflowuser
RUN mkdir -p /data/application
RUN touch /app/runtime.log && chown ragflowuser:ragflowuser /app/runtime.log
USER ragflowuser
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
