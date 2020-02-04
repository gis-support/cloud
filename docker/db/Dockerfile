FROM kartoza/postgis:12.0
RUN rm -rf /var/lib/apt/lists/* && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales
RUN sed -i -e 's/# pl_PL.UTF-8 UTF-8/pl_PL.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=pl_PL.UTF-8
COPY ./docker/db/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
COPY ./docker/db/init.sql /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init.sql
COPY ./docker/db/restore.sh /restore
COPY ./docker/db/dump.sh /dump
ENV LANG pl_PL.UTF-8