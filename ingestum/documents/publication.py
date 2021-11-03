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

    :param type: Identifier for the document
    :type type: str
    :param title: Human readable title for this document
    :type title: str
    :param context: Free-form dictionary with miscellaneous metadata provided by the transformers
    :type context: Optional[dict]
    :param origin: Document origin
    :type origin: Optional[str]
    :param version: Ingestum version
    :type version: str

    :param abstract: The publication's abstract
    :type abstract: str
    :param keywords: Keywords cited in the publication
    :type keywords: List[str]
    :param authors: Authors and their affiliation information
    :type authors: List[Author]
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
    :param provider_url: Link to the publication on the provider's website
    :type provider_url: str
    :param country: Country of publication
    :type country: str
    :param publication_type: Type of document published
    :type publication_type: List[str]
    :param full_text_url: Link to the full-text document
    :type full_text_url: str
    :param coi_statement: Conflict of interest statement as provided by the publisher
    :type coi_statement: str
    :param doi: Digital Object Identifier
    :type doi: str
    :param copyright: Copyright statement provided by the publisher of the journal
    :type copyright: str
    """

    type: Literal["publication"] = "publication"
    abstract: str = ""
    keywords: List[str] = []
    authors: List[Author] = []
    language: str = ""
    publication_date: str = ""
    journal: str = ""
    journal_ISSN: str = ""
    journal_volume: str = ""
    journal_issue: str = ""
    references: List[str] = []
    entrez_date: str = ""
    provider: str = ""
    provider_id: str = ""
    provider_url: str = ""
    country: str = ""
    publication_type: List[str] = []
    full_text_url: str = ""
    coi_statement: str = ""
    doi: str = ""
    copyright: str = ""
    pagination: str = ""

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
            kargs["authors"] = _object.authors

        if "language" in kargs:
            pass
        elif hasattr(_object, "language"):
            kargs["language"] = _object.language

        if "publication_date" in kargs:
            pass
        elif hasattr(_object, "publication_date"):
            kargs["publication_date"] = _object.publication_date

        if "journal" in kargs:
            pass
        elif hasattr(_object, "journal"):
            kargs["journal"] = _object.journal

        if "journal_ISSN" in kargs:
            pass
        elif hasattr(_object, "journal_ISSN"):
            kargs["journal_ISSN"] = _object.journal_ISSN

        if "journal_volume" in kargs:
            pass
        elif hasattr(_object, "journal_volume"):
            kargs["journal_volume"] = _object.journal_volume

        if "journal_issue" in kargs:
            pass
        elif hasattr(_object, "journal_issue"):
            kargs["journal_issue"] = _object.journal_issue

        if "references" in kargs:
            pass
        elif hasattr(_object, "references"):
            kargs["references"] = _object.references

        if "entrez_date" in kargs:
            pass
        elif hasattr(_object, "entrez_date"):
            kargs["entrez_date"] = _object.entrez_date

        if "provider" in kargs:
            pass
        elif hasattr(_object, "provider"):
            kargs["provider"] = _object.provider

        if "provider_id" in kargs:
            pass
        elif hasattr(_object, "provider_id"):
            kargs["provider_id"] = _object.provider_id

        if "provider_url" in kargs:
            pass
        elif hasattr(_object, "provider_url"):
            kargs["provider_url"] = _object.provider_url

        if "country" in kargs:
            pass
        elif hasattr(_object, "country"):
            kargs["country"] = _object.country

        if "publication_type" in kargs:
            pass
        elif hasattr(_object, "publication_type"):
            kargs["publication_type"] = _object.publication_type

        if "full_text_url" in kargs:
            pass
        elif hasattr(_object, "full_text_url"):
            kargs["full_text_url"] = _object.full_text_url

        if "coi_statement" in kargs:
            pass
        elif hasattr(_object, "coi_statement"):
            kargs["coi_statement"] = _object.coi_statement

        if "doi" in kargs:
            pass
        elif hasattr(_object, "doi"):
            kargs["doi"] = _object.doi

        if "copyright" in kargs:
            pass
        elif hasattr(_object, "copyright"):
            kargs["copyright"] = _object.copyright

        if "pagination" in kargs:
            pass
        elif hasattr(_object, "pagination"):
            kargs["pagination"] = _object.pagination

        return super().new_from(_object, **kargs)
