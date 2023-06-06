#!/bin/bash

# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: CC0-1.0

set -x

echo "# STARTING update.sh"
[ -f /tmp/update-running ] && return
touch /tmp/update-running
cd /code
python download.py batch
python to-numpy-data.py
rm /tmp/update-running
echo "# TERMINATING update.sh"

exit 0
