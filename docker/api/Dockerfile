FROM python:3.7.3
RUN apt-get remove -y binutils
# Add unstable repo to allow us to access latest GDAL builds
RUN echo deb http://ftp.uk.debian.org/debian unstable main contrib non-free >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get -t unstable install -y libgdal-dev g++
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
RUN pip install pipenv GDAL==2.4.2
COPY ./docker/api/start.sh ./
RUN chmod +x ./start.sh
COPY ./docker/api/prod_start.sh ./
RUN chmod +x ./prod_start.sh
COPY ./docker/api/tests.sh /usr/bin/tests
RUN chmod +x /usr/bin/tests
COPY ./docker/api/cli.sh /usr/bin/cli
RUN chmod +x /usr/bin/cli
COPY ./api ./api