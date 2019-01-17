FROM debian:stretch

MAINTAINER ping@mirceaulinic.net

ARG version="2017.7.8"

COPY --from=napalmautomation/napalm /usr/lib/python2.7/dist-packages/ /usr/lib/python2.7/dist-packages/
COPY --from=napalmautomation/napalm /usr/local/lib/python2.7/dist-packages/ /usr/local/lib/python2.7/dist-packages/

COPY ./ /var/cache/salt-napalm/
RUN apt-get update \
 && apt-get install -y python-pip \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

# Install min deps
RUN apt-get update \
 && apt-get install -y apt-utils \
                       wget \
                       gnupg \
 && echo 'deb http://httpredir.debian.org/debian stretch-backports main' >> /etc/apt/sources.list \
 && echo 'deb http://repo.saltstack.com/apt/debian/9/amd64/2017.7 stretch main' >> /etc/apt/sources.list.d/saltstack.list \
 && wget -O - https://repo.saltstack.com/apt/debian/9/amd64/2017.7/SALTSTACK-GPG-KEY.pub | apt-key add - \
 && apt-get update \
 && apt-get install -y python-zmq \
                       salt-master=$version+ds-2 \
                       python-pip \
 && pip install ansible \
 && pip install /var/cache/salt-napalm/ \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

COPY ./roster /etc/salt/roster
COPY ./master /etc/salt/master
