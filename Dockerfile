FROM python:latest as builder

WORKDIR /builder
COPY . /builder
RUN apt-get update && apt-get install -y python3-pip \
    && bash build_static.sh

FROM nginx:alpine

COPY --from=builder /builder/public /usr/share/nginx/html/

EXPOSE 80
