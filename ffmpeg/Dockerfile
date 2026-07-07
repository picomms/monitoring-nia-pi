FROM jrottenberg/ffmpeg:8.1-ubuntu

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    jq \
    iputils-ping \
    ca-certificates \
    ntpstat && \
	rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /bin

ADD ./run.sh run.sh

RUN chmod +x run.sh

RUN uv venv --clear && \
    uv pip install pyvimeo dotenv influxdb-client fractions dataclasses pathlib

ENV PATH="/bin/.venv/bin:$PATH"

CMD ["/bin/run.sh"]
