FROM jenkinsci/jenkins:2.150.1
USER root

##for -v docker 
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y sudo libltdl-dev \
    && apt-get -y install python3 \
    && apt-get -y install python3-pip \
    && apt-get -y install rsync \
    && rm -rf /var/lib/apt/lists/*

RUN echo "jenkins ALL=NOPASSWD: ALL" >> /etc/sudoers

#install python dep
COPY ./docker.py/dependence.sh /
RUN bash /dependence.sh