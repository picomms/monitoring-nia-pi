FROM telegraf:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    jq \
    iputils-ping \
    ntpstat && \
	rm -rf /var/lib/apt/lists/*
