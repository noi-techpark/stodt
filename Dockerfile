FROM python:3.7-slim as base

RUN mkdir -p /code
WORKDIR /code

COPY requirements .
RUN pip install -r requirements

RUN apt-get update -y \
 && apt-get upgrade -y
RUN apt-get install -y cron


# DEV stage ###################################################################
FROM base AS dev

ARG JENKINS_GROUP_ID=1000
ARG JENKINS_USER_ID=1000

RUN groupadd --gid $JENKINS_GROUP_ID jenkins && \
    useradd --uid $JENKINS_USER_ID --gid $JENKINS_GROUP_ID --create-home jenkins

# Not for BASE, because we do not need maven package caches for production
CMD [ "python" ]

# BUILD stage #################################################################
FROM base as build

RUN (crontab -l 2>/dev/null; echo "1 0 * * * /code/update.sh") | crontab -

COPY . /code
