FROM jenkinsci/jenkins:2.137
USER root

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak 
COPY gwf-source.list  /etc/apt/sources.list

##for -v docker 
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y sudo libltdl-dev \
    && rm -rf /var/lib/apt/lists/*

###for .net sdk
RUN  apt-get update \
     && apt-get install curl libunwind8 gettext apt-transport-https 

RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg \ 
     && mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg  \
     &&  sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-debian-stretch-prod stretch main" > /etc/apt/sources.list.d/dotnetdev.list'

RUN apt-get update && apt-get install dotnet-sdk-2.1 -y

RUN echo "jenkins ALL=NOPASSWD: ALL" >> /etc/sudoers

#使用tools里面的bulter plugin import 来替代...
#COPY plugins.txt /usr/share/jenkins/plugins.txt
#RUN /usr/local/bin/plugins.sh /usr/share/jenkins/plugins.txt

#install python dep
COPY ./docker.py/dependence.sh /
RUN bash /dependence.sh

### for git
RUN  git config --global user.email "jenkins@me.com" \
	&& git config --global user.name "jenkinsci"

###copy sshkeys
RUN mkdir -p /root/.ssh
COPY ./sshkeys/jenkinsci /root/.ssh/id_rsa
COPY ./sshkeys/jenkinsci.pub /root/.ssh/id_rsa.pub
RUN chmod 700 ~/.ssh/id_rsa

##node..
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -  \
    &&  apt-get install -y nodejs                            \   
    &&  apt-get install -y build-essential

#install yarn package
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - \
    &&  echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list  \
    &&  apt-get update && apt-get install yarn


#fornuget
RUN mkdir -p /root/.nuget/NuGet
COPY ./NuGet.config /root/.nuget/NuGet/NuGet.config

##tools
RUN apt-get install rsync -y