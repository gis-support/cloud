FROM nginx:latest
RUN apt-get update && apt-get install -y \
    curl
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash
RUN apt-get install -y nodejs git
COPY ./docker/nginx/prod_start.sh ./
RUN chmod +x ./prod_start.sh
COPY ./frontend /cloud
COPY ./docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf