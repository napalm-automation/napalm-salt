FROM debian:stretch

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
                        salt-master=$version+ds-2 \
  && rm -rf /var/lib/apt/lists/*

COPY ./master /etc/salt/master

# Add Run File
ADD run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

# Ports
EXPOSE 4505 4506

# Run Command
CMD "/usr/local/bin/run.sh"
