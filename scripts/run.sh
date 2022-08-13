#!/bin/bash

clear

# delete the useless index.html file that is downloaded
if [ -f index.html ]; then
    rm index.html
    clear
fi

# source each script one at a time
. exact-blacklist.sh && \
. exact-whitelist.sh && \
. regex-blacklist.sh && \
. regex-whitelist.sh
