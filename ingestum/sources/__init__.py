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
from . import local
from . import html
from . import pdf
from . import image
from . import text
from . import xml
from . import csv
from . import xls
from . import audio
from . import twitter
from . import document
from . import email
from . import proquest
from . import docx
from . import pubmed
from . import reddit
from . import litcovid
from . import biorxiv
from . import europepmc
from . import pptx

Base = base.BaseSource
Local = local.LocalSource
HTML = html.Source
PDF = pdf.Source
Image = image.Source
Text = text.Source
XML = xml.Source
CSV = csv.Source
XLS = xls.Source
Audio = audio.Source
Twitter = twitter.Source
Document = document.Source
Email = email.Source
ProQuest = proquest.Source
DOCX = docx.Source
PubMed = pubmed.Source
Reddit = reddit.Source
LitCovid = litcovid.Source
Biorxiv = biorxiv.Source
EuropePMC = europepmc.Source
PPTX = pptx.Source

# Load plugins
manager.default.register(sys.modules[__name__], "sources", Base)
