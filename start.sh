#!/bin/bash

# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: CC0-1.0

cron
echo Switching to new host '$HOST'
sed -ie 's%http://localhost:5000%'$HOST'%g' www/index.html
python /code/app.py
