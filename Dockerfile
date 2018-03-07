FROM debian:stretch

MAINTAINER ping@mirceaulinic.net

WORKDIR /etc

## Install min deps
RUN apt-get update \
  && apt-get install -y apt-utils \
  && apt-get install -y wget \
  && apt-get install -y gnupg \
  && apt-get install -y git \
  && rm -rf /var/lib/apt/lists/*

## Setup sources for Jessie backports and SaltStack repo
RUN echo 'deb http://httpredir.debian.org/debian stretch-backports main' >> /etc/apt/sources.list \
    && echo 'deb http://repo.saltstack.com/apt/debian/9/amd64/latest stretch main' >> /etc/apt/sources.list.d/saltstack.list \
    && wget -O - https://repo.saltstack.com/apt/debian/9/amd64/latest/SALTSTACK-GPG-KEY.pub | apt-key add - \
    && apt-get update

## Install backports
RUN apt-get install -y python-zmq

## Install Salt packages
## salt-proxy is already included in salt-minion when installing from the SaltStack repos
## if installing from the official Debian, salt-proxy must be install as a separate package
RUN apt-get install -y salt-master=2017.7.4+ds-1 \
    && apt-get install -y salt-minion=2017.7.4+ds-1

# Install a text editor
RUN apt-get install -y vim

## Creating Salt pillar_roots and file_roots directories
RUN mkdir /etc/salt/pillar \
    && mkdir /etc/salt/states \
    && mkdir /etc/salt/templates \
    && mkdir /etc/salt/reactors \
    && mkdir /etc/salt/_modules \
    && mkdir /etc/salt/_beacons

## Copy config files and extension modules
WORKDIR /etc/salt
ADD master master
ADD proxy proxy
ADD oxygen/_modules/* /etc/salt/_modules/
ADD oxygen/_beacons/* /etc/salt/_beacons/

## Install NAPALM & underlying libraries dependencies
## Will install all NAPALM sub-libraries
## But the user is welcome to install only the libraries they require
RUN apt-get install -y python-cffi python-dev libxslt1-dev libssl-dev libffi-dev \
    && apt-get install -y python-pip \
    && pip install -U cffi \
    && pip install -U cryptography \
    && pip install napalm

# Add Run File
ADD run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

# Ports
EXPOSE 4505 4506

# Run Command
CMD "/usr/local/bin/run.sh"
