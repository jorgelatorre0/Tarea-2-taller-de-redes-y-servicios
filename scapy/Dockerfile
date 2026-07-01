FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    iproute2 \
    iputils-ping \
    net-tools \
    tcpdump \
    iptables \
    nano \
    libnetfilter-queue-dev \
    libnfnetlink-dev \
    libmnl-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages scapy netfilterqueue
WORKDIR /root
CMD ["/bin/bash"]
