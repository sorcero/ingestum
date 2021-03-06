##
## Copyright (c) 2020 Sorcero, Inc.
##
## This file is part of Sorcero's Language Intelligence platform
## (see https://www.sorcero.com).
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.
##

export INGESTUM_PLUGINS_DIR=tests/plugins/

echo "Setting up environment..."
virtualenv env > /dev/null
source env/bin/activate > /dev/null
pip install . > /dev/null
ingestum-install-plugins > /dev/null

pyflakes scripts ingestum tests tools && \
black --check scripts ingestum tests tools && \
python3 -m pytest
