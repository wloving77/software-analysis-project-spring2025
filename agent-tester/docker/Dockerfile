# docker/Dockerfile
FROM klee/klee:3.0

ENV DEBIAN_FRONTEND=noninteractive

USER root

# Add Kitware GPG key to fix apt warning
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 16FAAD7AF99A65E2

# ------------------------------
# 1. Install extra dependencies
# ------------------------------
RUN apt-get update && apt-get install -y \
    build-essential cmake git curl wget \
    python3 python3-pip \
    zlib1g-dev libz3-dev libboost-all-dev \
    autoconf libtool flex bison bc \
    libsqlite3-dev python3-setuptools \
    libgmp-dev pkg-config help2man \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------
# 2. Install AFL++
# ------------------------------
RUN git clone https://github.com/AFLplusplus/AFLplusplus.git /afl && \
    cd /afl && make distrib && make install

# ------------------------------
# 3. Install Python dependencies
# ------------------------------

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# ------------------------------
# 4. Set up working directory
# ------------------------------
COPY . /agent-tester
WORKDIR /agent-tester

CMD ["/bin/bash"]
