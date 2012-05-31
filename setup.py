#!/usr/bin/env python -t3
# -*- coding: utf-8 -*-

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

#from upkern.doc.man import build_manpage

setup_params = {}
setup_params['name'] = "pmort"
setup_params['version'] = "9999"
setup_params['description'] = "".join([
    "A daemon that collects information useful for a post-mortem analysis on ",
    "a server."
    ])
setup_params["long_description"] = "".join([
    "Daemonized system information collection tool for performing post-mortem ",
    "analysis on various components of the system.  Is pluggable with various ",
    "scripts that execute to obtain said information.",
    ])
setup_params['author'] = "Alex Brandt"
setup_params['author_email'] = "alunduil@alunduil.com"
setup_params['url'] = "http://www.alunduil.com/programs/pmort/"
setup_params['license'] = "GPL-2"
setup_params['scripts'] = [
        "bin/pmort",
        ]
setup_params['packages'] = [
        "pmort",
        "pmort.parameters",
        "pmort.plugins",
        ]
setup_params['data_files'] = [
        ("share/doc/%s-%s" % (setup_params['name'], setup_params['version']), [
            "README",
            ]),
        ("share/doc/%s-%s/config" % (setup_params['name'], setup_params['version']), [
            "config/pmort.conf",
            "config/init.gentoo",
            "config/logrotate.conf",
            ]),
#        ("share/man/man1", [
#            "doc/man/man1/ssync.1",
#            ]),
        ]
setup_params['requires'] = [
        ]
#setup_params['cmdclass'] = {
#        "build_manpage": build_manpage,
#        }

setup(**setup_params)

