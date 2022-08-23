#!/bin/bash

# to be used with: https://github.com/yunchih/static-binaries

## remove any packages you dont want to install from the FILES array below
FILES=( entr fio fping iozone iperf2 iperf3 lp lpr nc PortFusion strace tcpdump tftp wget )

## install the packages
for i in ${FILES[@]}; do
    wget https://raw.githubusercontent.com/yunchih/static-binaries/master/$i -O /tmp/$i && chmod +x /tmp/$i
done

## replace the below command with the one above to test the output.
# echo "wget https://raw.githubusercontent.com/yunchih/static-binaries/master/$i -O /tmp/$i && chmod +x /tmp/$i"
