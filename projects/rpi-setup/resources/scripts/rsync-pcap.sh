#!/bin/bash

source=/mnt/external/pcaps
target=root@10.4.4.2:/data/pcaps/`/bin/hostname`

/usr/bin/find $source -mmin +15 -printf "%f\n" | /usr/bin/rsync --log-file=$source/rsync-`/bin/date +%Y%m%d-%H%M%S`.log -e ssh --compress --remove-source-files --files-from=- $source $target

