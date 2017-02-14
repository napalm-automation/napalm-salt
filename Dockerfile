FROM debian:jessie

MAINTAINER mircea@cloudflare.com

WORKDIR /etc

# Install min deps
RUN apt-get update \
  && apt-get install -y apt-utils \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

## Setup sources for Salt backports and official repo
RUN echo 'deb http://httpredir.debian.org/debian jessie-backports main' >> /etc/apt/sources.list \
    && echo 'deb http://httpredir.debian.org/debian stretch main' >> /etc/apt/sources.list \
    && echo 'deb http://repo.saltstack.com/apt/debian/8/amd64/latest jessie main' >> /etc/apt/sources.list.d/saltstack.list \
    && wget -O - https://repo.saltstack.com/apt/debian/8/amd64/latest/SALTSTACK-GPG-KEY.pub | apt-key add - \
    && apt-get update

## Install Salt backports
RUN apt-get install -y --force-yes python-zmq python-systemd/jessie-backports python-tornado/jessie-backports salt-common/stretch \

## Install Salt packages
RUN apt-get install -y --force-yes salt-master \
    && apt-get install -y --force-yes salt-minion \
    && apt-get install -y --force-yes salt-proxy

## Creating Salt pillar_roots and file_roots directories
RUN mkdir /etc/salt/pillar \
    && mkdir /etc/salt/states \
    && mkdir /etc/salt/templates \
    && mkdir /etc/salt/reactors \
    && mkdir /etc/salt/extmods \
    && mkdir /etc/salt/extmods/_modules \
    && mkdir /etc/salt/extmods/_states \
    && mkdir /etc/salt/extmods/_output \
    && mkdir /etc/salt/extmods/_runners

## Copy proxy systemd files
ADD salt-proxy@.service systemd/system/salt-proxy@.service

## Copy config files and extension modules
WORKDIR /etc/salt
ADD master master
ADD proxy proxy
ADD nitrogen/_modules/* /etc/salt/extmods/_modules/
ADD nitrogen/_states/* /etc/salt/extmods/_states/
ADD nitrogen/_output/* /etc/salt/extmods/_output/
ADD nitrogen/_runners/* /etc/salt/extmods/_runners/

## Install NAPALM & underlying libraries dependencies
## Will install all NAPALM sub-libraries
## But the user is welcome to install only the libraries they require
RUN apt-get install -y --force-yes python-cffi python-dev libxslt1-dev libssl-dev libffi-dev \
    && apt-get install -y --force-yes python-pip \
    && pip install -U cffi \
    && pip install -U cryptography \
    && pip install napalm
