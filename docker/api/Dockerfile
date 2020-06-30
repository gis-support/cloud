FROM python:3.8.3
# Removing libs causing conflicts
RUN apt-get remove -y binutils libgcc-8-dev
# Add unstable repo to allow us to access latest GDAL builds
RUN echo deb http://ftp.uk.debian.org/debian unstable main contrib non-free >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get -t unstable install -y libgdal-dev g++
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
RUN pip install pipenv gdal==3.0.4
COPY ./docker/api/start.sh ./
RUN chmod +x ./start.sh
COPY ./docker/api/prod_start.sh ./
RUN chmod +x ./prod_start.sh
COPY ./docker/api/tests.sh /usr/bin/tests
RUN chmod +x /usr/bin/tests
COPY ./docker/api/cli.sh /usr/bin/cli
RUN chmod +x /usr/bin/cli
COPY ./api ./api

COPY ./docker/api/migrate.sh /usr/bin/migrate
RUN chmod +x /usr/bin/migrate

COPY ./docker/api/init_database.sh /usr/bin/init_database
RUN chmod +x /usr/bin/init_database
