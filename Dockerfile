FROM python:latest as builder

COPY ./dx_static_convert_toml_to_json.py .
COPY ./public/tmp_wait_for_json_editor.toml .
RUN apt-get update && apt-get install -y python3-pip \
    && pip install toml \
    && python -u ./dx_static_convert_toml_to_json.py

FROM nginx:alpine

COPY ./public /usr/share/nginx/html/
COPY --from=builder tmp_wait_for_json_editor.json /usr/share/nginx/html/

EXPOSE 80
