FROM napalmautomation/napalm:latest

MAINTAINER ping@mirceaulinic.net

ARG version="2017.7.8"

## Install min deps
RUN apt-get update \
  && apt-get install -y apt-utils \
                        wget \
                        gnupg \
  && echo 'deb http://httpredir.debian.org/debian stretch-backports main' >> /etc/apt/sources.list \
  && echo 'deb http://repo.saltstack.com/apt/debian/9/amd64/2017.7 stretch main' >> /etc/apt/sources.list.d/saltstack.list \
  && wget -O - https://repo.saltstack.com/apt/debian/9/amd64/2017.7/SALTSTACK-GPG-KEY.pub | apt-key add - \
  && apt-get update \
  && apt-get install -y python-zmq \
                        salt-minion=$version+ds-2 \
  && rm -rf /var/lib/apt/lists/*

COPY ./proxy /etc/salt/proxy
