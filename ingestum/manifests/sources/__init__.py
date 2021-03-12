# -*- coding: utf-8 -*-

#
# Copyright (c) 2020 Sorcero, Inc.
#
# This file is part of Sorcero's Language Intelligence platform
# (see https://www.sorcero.com).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


import sys

from ingestum.plugins import manager

from . import base
from . import audio
from . import csv
from . import html
from . import image
from . import pdf
from . import text
from . import twitter
from . import xls
from . import xml
from . import document
from . import email
from . import proquest
from . import docx
from . import pubmed

Audio = audio.Source
CSV = csv.Source
HTML = html.Source
Image = image.Source
PDF = pdf.Source
Text = text.Source
Twitter = twitter.Source
XLS = xls.Source
XML = xml.Source
Document = document.Source
Email = email.Source
ProQuest = proquest.Source
DOCX = docx.Source
PubMed = pubmed.Source

# Load plugins
manager.default.register(sys.modules[__name__], "manifests.sources", base.BaseSource)
