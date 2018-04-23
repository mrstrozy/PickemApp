#!/usr/bin/env python

import os

os.system("pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start")
