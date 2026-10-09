FROM python:3.9-slim

RUN apt-get -qq update \
    && DEBIAN_FRONTEND="noninteractive" TZ="Europe/Zurich" apt-get install -y --no-install-recommends \
       wget \
    && rm -rf /var/lib/apt/lists/*

COPY --from=cbrg/darwin:latest /darwin /darwin
COPY --from=cbrg/darwin:latest /usr/local/bin/darwin /usr/bin/darwin

COPY lib /tmp/oma-lib

# The release workflow passes the tarball it just attached to the release and
# installs it unchanged. Other builds test the current lib/ on top of the
# latest published release.
ARG OMA_TARBALL_URL=
RUN cd /tmp && wget -O - "${OMA_TARBALL_URL:-https://omabrowser.org/standalone/OMA.latest.tgz}" | tar xzf - \
    && mv OMA.* OMA \
    && if [ -z "$OMA_TARBALL_URL" ] ; then cp /tmp/oma-lib/* OMA/lib/ ; fi \
    && sed -i -e "s/^# AuxDataPath.*/AuxDataPath := 'data\/';/" OMA/parameters.drw \
    && /tmp/OMA/install.sh /usr/local /oma/data \
    && rm -rf /tmp/OMA /tmp/oma-lib


ENV PATH /usr/local/OMA/bin:$PATH
ENV DARWIN_DATA_DIRECTORY /oma/data
WORKDIR /oma
CMD oma

