FROM ubuntu:bionic

ENV INSTALL_KEY=379CE192D401AB61

ENV DEB_DISTRO=bionic

RUN apt update && apt-get install python3 curl gnupg1 apt-transport-https dirmngr -y

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $INSTALL_KEY

RUN echo "deb https://ookla.bintray.com/debian ${DEB_DISTRO} main" | tee  /etc/apt/sources.list.d/speedtest.list

RUN apt-get update && apt-get install speedtest

WORKDIR /usr/src/app

COPY ./ookla /usr/src/app

RUN chmod +x ./index.py

CMD ["./index.py"]
