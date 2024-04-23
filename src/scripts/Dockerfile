############## Compatibility ############# 
# Debian-based Linux distributions, macOS, Windows
########## Building Steps ##############
# docker build -t meta_bio_detect .
# docker save -o MetaBioDetect_img.tar meta_bio_detect
########## Running app bash #############
# docker run -it meta_bio_detect /bin/bash 


# Python base image
FROM python:3.12.0

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    autoconf \
    automake \
    git \
    && apt-get clean

# Install vsearch
RUN git clone https://github.com/torognes/vsearch.git \
    && cd vsearch \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install

# Install cutadapt and matplotlib
RUN pip install cutadapt matplotlib

# Set working directory
WORKDIR /app

# Create a directory for user files input
RUN mkdir /app/uploads

# Copy pipelines scipts to the image
COPY . .



