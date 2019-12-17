FROM nginx:latest
RUN apt-get update && apt-get install -y \
    curl
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash
RUN apt-get install -y nodejs git
COPY ./frontend /cloud
COPY ./docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
RUN cd /cloud && npm i && npm run build