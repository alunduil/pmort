#!/usr/bin/env python -t3
#
# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# This program is free software; you can redistribute it and#or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA  02111-1307, USA.

from distutils.core import setup

try:
    from pmort import information
except ImportError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    from pmort import information

PARAMS = {}
PARAMS["name"] = information.NAME
PARAMS["version"] = information.VERSION
PARAMS["description"] = information.DESCRIPTION
PARAMS["long_description"] = information.LONG_DESCRIPTION
PARAMS["author"] = information.AUTHOR
PARAMS["author_email"] = information.AUTHOR_EMAIL
PARAMS["url"] = information.URL
PARAMS["license"] = information.LICENSE

PARAMS["scripts"] = [
        "bin/pmort",
        ]
PARAMS["packages"] = [
        "pmort",
        "pmort.plugins",
        ]
PARAMS["package_data"] = {
        "pmort.plugins": [
            "shell_scripts/*.sh",
            ],
        }
PARAMS["data_files"] = [
        ("share/doc/{P[name]}-{P[version]}".format(P = PARAMS), [
            "README.md",
            ]),
        ("share/doc/{P[name]}-{P[version]}/config".format(P = PARAMS), [
            "config/pmort.conf",
            "config/init.gentoo",
            "config/logrotate.conf",
            "config/pmort.cron",
            ]),
        ("share/man/man8", [
            "doc/man/man8/pmort.8",
            ]),
        ("share/man/man5", [
            "doc/man/man5/pmort.conf.5",
            ]),
        ]

PARAMS["requires"] = [
        "daemon",
        ]

setup(**PARAMS)
