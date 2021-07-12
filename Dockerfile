FROM python:3-slim

RUN apt-get -qq update \
    && DEBIAN_FRONTEND="noninteractive" TZ="Europe/Zurich" apt-get install -y --no-install-recommends \
       wget \
    && rm -rf /var/lib/apt/lists/*

COPY --from=cbrg/darwin:latest /darwin /darwin
COPY --from=cbrg/darwin:latest /usr/local/bin/darwin /usr/bin/darwin

RUN cd /tmp && wget -O - "https://omabrowser.org/standalone/OMA.latest.tgz" | tar xzf - \
    && mv OMA.* OMA \
    && sed -i -e "s/^# AuxDataPath.*/AuxDataPath := 'data\/';/" OMA/parameters.drw \
    && /tmp/OMA/install.sh /usr/local /oma/data \
    && rm -rf /tmp/OMA

ENV PATH /usr/local/OMA/bin:$PATH
ENV DARWIN_DATA_DIRECTORY /oma/data
WORKDIR /oma
CMD oma

