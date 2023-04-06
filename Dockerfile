FROM --platform=$BUILDPLATFORM python:3.11.3-slim-buster

LABEL org.opencontainers.image.title="check-filtering"
LABEL org.opencontainers.image.description="Check URLs that filtered ( or not ) in Iran"
LABEL org.opencontainers.image.url="https://github.com/hatamiarash7/CheckFiltering"
LABEL org.opencontainers.image.source="https://github.com/hatamiarash7/CheckFiltering"
LABEL org.opencontainers.image.vendor="hatamiarash7"
LABEL org.opencontainers.image.author="hatamiarash7"
LABEL org.opencontainers.version="$APP_VERSION"
LABEL org.opencontainers.image.created="$DATE_CREATED"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip3 install --no-cache-dir pip \
 && pip3 install --no-cache-dir -r requirements.txt

COPY ./check.py /app/

CMD ["python3", "check.py"]
