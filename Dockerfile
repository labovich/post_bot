FROM ubuntu:20.04

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt install -y --no-install-recommends apt-utils \
    && apt upgrade -y \
    && apt dist-upgrade -y \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN export DEBIAN_FRONTEND=noninteractive \
    && BUILD_DEPS='build-essential python3-dev' \
    && apt update \
    && apt install -y --no-install-recommends ${BUILD_DEPS} \
    && apt install -y --no-install-recommends \
      locales \
      python3 \
      python3-pip \
      python3-setuptools \
    && pip3 install --upgrade pip --no-cache-dir \
    && locale-gen en_US.UTF-8 \
    && pip3 install pipenv --no-cache-dir
    && apt clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /opt

COPY . /opt/app

RUN pipenv sync  \
    && apt autoremove -y ${BUILD_DEPS} \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT [ "pipenv", "run", "python", "main.py"]