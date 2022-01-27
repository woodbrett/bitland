#bitland testnet dockerfile
#author: Prakash Anandan
FROM ubuntu:20.10
LABEL author prakasha@gmail.com

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y upgrade &&\
    apt-get -y install wget &&\
    apt-get -y install gnupg2 &&\
    echo "deb http://apt.postgresql.org/pub/repos/apt/ groovy-pgdg main" | tee -a /etc/apt/sources.list.d/pgdg.list &&\
    wget https://www.postgresql.org/media/keys/ACCC4CF8.asc &&\
    apt-key add ACCC4CF8.asc &&\
    apt-get update &&\
    apt-get install -y postgresql-13 &&\
    apt-get install -y postgresql-13-postgis-3 &&\
    apt-get install -y python3 &&\
    apt-get install -y python3-pip &&\
    apt-get install -y libpq-dev python-dev &&\
    apt-get install -y git &&\
    mkdir /home/bitland_testnet &&\
    cd /home/bitland_testnet/ &&\
    git clone https://github.com/woodbrett/bitland.git &&\
    cd bitland &&\
    git checkout add_testnet &&\
    python3 -m pip install -r /home/bitland_testnet/bitland/requirements.txt &&\
    useradd "bitland_testnet"

USER postgres

RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER bitland_testnet WITH SUPERUSER PASSWORD 'password';" &&\
    createdb -O bitland_testnet bitland_testnet &&\
    echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/13/main/pg_hba.conf &&\
    x=`echo "local all  all    md5"; cat /etc/postgresql/13/main/pg_hba.conf` &&\
    echo "$x" > /etc/postgresql/13/main/pg_hba.conf &&\
    echo "listen_addresses='*'" >> /etc/postgresql/13/main/postgresql.conf &&\
    /etc/init.d/postgresql reload &&\
    PGPASSWORD=password psql -U bitland_testnet -d bitland_testnet -a -f /home/bitland_testnet/bitland/documentation/database_etl.sql

USER root
EXPOSE 5432
EXPOSE 8334
ENV DEBIAN_FRONTEND newt

