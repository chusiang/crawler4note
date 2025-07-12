FROM python:3.7-alpine

LABEL org.opencontainers.image.authors="chusiang@drx.tw"

COPY *.py LICENSE README.md requirements.txt /srv/

RUN echo "===> Install pip packages from requirements.txt ..."  && \
      pip3 install -r /srv/requirements.txt

RUN echo "===> Removing package cache ..."  && \
      rm -rf /var/cache/apk/*               && \
      rm -rf ~/.cache/pip

ONBUILD RUN echo "===> Updating TLS certificates ..."  && \
      apk add --update --no-cache openssl ca-certificates

WORKDIR /srv

CMD [ "python", "--version" ]
