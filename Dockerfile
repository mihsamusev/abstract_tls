FROM ubuntu:18.04
WORKDIR /home
# Basic
RUN apt-get update \
    && apt-get install -y software-properties-common curl git

# SUMO
RUN apt-get update \
    && add-apt-repository ppa:sumo/stable \
    && apt-get install -y sumo sumo-tools
ENV SUMO_HOME=/usr/share/sumo/

# miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b \
    && rm -f rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}

RUN conda update -y conda \
    && conda init \
    && conda install -y pip pytest
    
COPY environment.yml /home/
RUN conda env create -f environment.yml




