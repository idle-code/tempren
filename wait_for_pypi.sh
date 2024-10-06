#!/bin/bash
set -eux

PACKAGE_NAME=$1
PACKAGE_VERSION=$2
TIMEOUT=$3
DELAY_BETWEEN_REQUESTS=$4

declare URL=https://pypi.org/project/$PACKAGE_NAME/$PACKAGE_VERSION/

DELAY_BETWEEN_REQUESTS=$DELAY_BETWEEN_REQUESTS \
URL=$URL STATUS=200 timeout \
  --foreground -s TERM $TIMEOUT bash -c \
    'while [[ ${STATUS_RECEIVED} != ${STATUS} ]];\
        do STATUS_RECEIVED=$(curl -s -o /dev/null -L -w ''%{http_code}'' ${URL}) && \
        echo "received status: $STATUS_RECEIVED" && \
        sleep $DELAY_BETWEEN_REQUESTS;\
    done;
    echo success with status: $STATUS_RECEIVED'
