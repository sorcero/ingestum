# -*- coding: utf-8 -*-

#
# Copyright (c) 2021 Sorcero, Inc.
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


import copy

from .base import BaseDocument
from pydantic import BaseModel
from typing import List
from typing_extensions import Literal


class Author(BaseModel):
    """
    The Author model

    :param name: Author's normalized name
    :type name: str
    :param affiliation: Author's affiliation information
    :type affiliation: List[str]
    """

    name: str = ""
    affiliation: List[str] = []


class Document(BaseDocument):
    """
    Class to support publication documents

    :param abstract: The publication's abstract
    :type abstract: str
    :param keywords: Keywords cited in the publication
    :type keywords: List[str]
    :param authors: Authors and their affiliation information
    :type authors: List[Dict]
    :param language: Language in which the publication is written
    :type language: str
    :param publication_date: The publication's publication date
    :type publication_date: str
    :param journal: Journal in which the publication was published
    :type journal: str
    :param journal_ISSN: The journal's ISSN
    :type journal_ISSN: str
    :param references: References cited in the publication
    :type references: List[str]
    :param entrez_date: Date the publication was added to PubMed
    :type entrez_date: str
    :param provider: Source/provider of the publication
    :type provider: str
    :param provider_id: Provider-specific ID of the publication
    :type provider_id: str
    :param provider_link: Link to the publication on the provider's website
    :type provider_link: str
    :param country: Country of publication
    :type country: str
    :param publication_type: Type of document published
    :type publication_type: List[str]
    """

    type: Literal["publication"] = "publication"
    abstract: str = ""
    keywords: List[str] = []
    authors: List[Author] = []
    language: str = ""
    publication_date: str = ""
    journal: str = ""
    journal_ISSN: str = ""
    references: List[str] = []
    entrez_date: str = ""
    provider: str = ""
    provider_id: str = ""
    provider_link: str = ""
    country: str = ""
    publication_type: List[str] = []

    @classmethod
    def new_from(cls, _object, **kargs):
        if "abstract" in kargs:
            pass
        elif hasattr(_object, "abstract"):
            kargs["abstract"] = _object.abstract

        if "keywords" in kargs:
            pass
        elif hasattr(_object, "keywords"):
            kargs["keywords"] = _object.keywords

        if "authors" in kargs:
            pass
        elif hasattr(_object, "authors"):
            kargs["authors"] = copy.deepcopy(_object.authors)

        if "language" in kargs:
            pass
        elif hasattr(_object, "language"):
            kargs["language"] = copy.deepcopy(_object.language)

        if "publication_date" in kargs:
            pass
        elif hasattr(_object, "publication_date"):
            kargs["publication_date"] = copy.deepcopy(_object.publication_date)

        if "journal" in kargs:
            pass
        elif hasattr(_object, "journal"):
            kargs["journal"] = copy.deepcopy(_object.journal)

        if "journal_ISSN" in kargs:
            pass
        elif hasattr(_object, "journal_ISSN"):
            kargs["journal_ISSN"] = copy.deepcopy(_object.journal_ISSN)

        if "references" in kargs:
            pass
        elif hasattr(_object, "references"):
            kargs["references"] = copy.deepcopy(_object.references)

        if "entrez_date" in kargs:
            pass
        elif hasattr(_object, "entrez_date"):
            kargs["entrez_date"] = copy.deepcopy(_object.references)

        if "provider" in kargs:
            pass
        elif hasattr(_object, "provider"):
            kargs["provider"] = copy.deepcopy(_object.references)

        if "provider_id" in kargs:
            pass
        elif hasattr(_object, "provider_id"):
            kargs["provider_id"] = copy.deepcopy(_object.references)

        if "provider_link" in kargs:
            pass
        elif hasattr(_object, "provider_link"):
            kargs["provider_link"] = copy.deepcopy(_object.references)

        if "country" in kargs:
            pass
        elif hasattr(_object, "country"):
            kargs["country"] = copy.deepcopy(_object.references)

        if "publication_type" in kargs:
            pass
        elif hasattr(_object, "publication_type"):
            kargs["publication_type"] = copy.deepcopy(_object.references)

        return super().new_from(_object, **kargs)
