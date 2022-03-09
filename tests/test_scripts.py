# -*- coding: utf-8 -*-

#
# Copyright (c) 2020,2021 Sorcero, Inc.
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

# This file is part of Sorcero's Language Intelligence platform and is

import os
import sys
import pytest

__script__ = os.path.dirname(os.path.realpath(__file__))
__scripts__ = os.path.join(__script__, "..", "scripts")

sys.path.insert(0, __scripts__)

import pipeline_annotation
import pipeline_audio
import pipeline_csv
import pipeline_xls
import pipeline_html
import pipeline_image
import pipeline_ocr
import pipeline_pdf
import pipeline_pdf_publication
import pipeline_text
import pipeline_twitter_form
import pipeline_twitter_publication
import pipeline_xml
import pipeline_document
import pipeline_email
import pipeline_proquest_xml
import pipeline_proquest_publication
import pipeline_rss
import pipeline_docx
import pipeline_unstructured_form
import pipeline_pubmed_xml
import pipeline_pubmed_text
import pipeline_pubmed_publication
import pipeline_reddit_form
import pipeline_reddit_publication
import pipeline_litcovid_publication
import pipeline_biorxiv_publication
import pipeline_europepmc_publication
import pipeline_pptx

from tests import utils


Annotation_data = "tests/data/test.pdf"
Audio_data = "tests/data/test.wav"
CSV_data = "tests/data/test.csv"
XLS_data = "tests/data/test.xlsx"
HTML_data = "tests/data/test.html"
Image_data = "tests/data/test.jpg"
OCR_data = "tests/data/test.pdf"
PDF_data = "tests/data/test.pdf"
PDF_publication_data = "tests/data/test_pdf_publication.pdf"
Text_data = "tests/data/test.txt"
XML_data = "tests/data/test.xml"
Document_data = "tests/output/script_pipeline_document.json"
DOCX_data = "tests/data/test.docx"
UForm_data = "tests/data/unstructured_form.pdf"
PPTX_data = "tests/data/test.pptx"


@pytest.mark.skipif(utils.skip_twitter, reason="INGESTUM_TWITTER_* variables not found")
def test_pipeline_twitter_form():
    document = pipeline_twitter_form.ingest("twitter", 10, "recent", [])
    assert len(document.dict()["content"]) > 0


@pytest.mark.skipif(utils.skip_twitter, reason="INGESTUM_TWITTER_* variables not found")
def test_pipeline_twitter_publication():
    document = pipeline_twitter_publication.ingest("twitter", 10, "recent", [])
    assert len(document.dict()["content"]) > 0


def test_pipeline_text():
    document = pipeline_text.ingest(Text_data)
    assert document.dict() == utils.get_expected("script_pipeline_text")


def test_pipeline_xml():
    document = pipeline_xml.ingest(XML_data)
    assert document.dict() == utils.get_expected("script_pipeline_xml")


def test_pipeline_csv():
    document = pipeline_csv.ingest(CSV_data)
    assert document.dict() == utils.get_expected("script_pipeline_csv")


def test_pipeline_xls():
    document = pipeline_xls.ingest(XLS_data)
    assert document.dict() == utils.get_expected("script_pipeline_xls")


def test_pipeline_html():
    document = pipeline_html.ingest(HTML_data, "body", "")
    assert document.dict() == utils.get_expected("script_pipeline_html")


def test_pipeline_image():
    document = pipeline_image.ingest(Image_data)
    assert document.dict() == utils.get_expected("script_pipeline_image")


def test_pipeline_ocr():
    document = pipeline_ocr.ingest(OCR_data, 1, 3)
    assert document.dict() == utils.get_expected("script_pipeline_ocr")


def test_pipeline_pdf():
    document = pipeline_pdf.ingest(PDF_data, 1, 3)
    assert document.dict() == utils.get_expected("script_pipeline_pdf")


@pytest.mark.skipif(utils.skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_pdf_publication():
    document = pipeline_pdf_publication.ingest(PDF_publication_data, -1, -1).dict()
    del document["abstract"]
    del document["content"]

    assert document == utils.get_expected("script_pipeline_pdf_publication")


def test_pipeline_pdf_no_pages():
    document = pipeline_pdf.ingest(PDF_data, None, None)
    assert document.dict() == utils.get_expected("script_pipeline_pdf")


def test_pipeline_audio():
    document = pipeline_audio.ingest(Audio_data)
    assert document.dict() == utils.get_expected("script_pipeline_audio")


def test_pipeline_annotation():
    document = pipeline_annotation.ingest(Annotation_data, 1, 1)
    assert document.dict() == utils.get_expected("script_pipeline_annotation")


def test_pipeline_document():
    document = pipeline_document.ingest(Document_data)
    assert document.dict() == utils.get_expected("script_pipeline_document")


@pytest.mark.skipif(utils.skip_email, reason="INGESTUM_EMAIL_* variables not found")
def test_pipeline_email():
    document = pipeline_email.ingest(24, "test@test.test", "subject", "body")
    assert document.dict() == utils.get_expected("script_pipeline_email")


@pytest.mark.skipif(
    utils.skip_proquest, reason="INGESTUM_PROQUEST_* variables not found"
)
def test_pipeline_proquest_xml():
    document = pipeline_proquest_xml.ingest(
        "Cardiothyrosis. Presentation of a clinical case", ["medlineprof"], 1
    ).dict()

    del document["context"]["proquest_source_create_xml_collection_document"][
        "timestamp"
    ]

    assert document["content"][0]["content"] != ""
    del document["content"][0]["content"]

    # We can't compare the 'origin' because it changes for each request
    assert document["content"][0]["origin"] != ""
    del document["content"][0]["origin"]

    assert document == utils.get_expected("script_pipeline_proquest_xml")


@pytest.mark.skipif(
    utils.skip_proquest, reason="INGESTUM_PROQUEST_* variables not found"
)
def test_pipeline_proquest_publication():
    document = pipeline_proquest_publication.ingest(
        "Cardiothyrosis. Presentation of a clinical case", ["medlineprof"], 1
    ).dict()

    del document["context"]["proquest_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document["content"][0]["abstract"] != ""
    del document["content"][0]["abstract"]

    # We can't compare the 'origin' because it changes for each request
    assert document["content"][0]["origin"] != ""
    del document["content"][0]["origin"]

    assert document == utils.get_expected("script_pipeline_proquest_publication")


def test_pipeline_docx():
    document = pipeline_docx.ingest(DOCX_data)
    assert document.dict() == utils.get_expected("script_pipeline_docx")


def test_pipeline_unstructured_form():
    document = pipeline_unstructured_form.ingest(UForm_data, 1, 1)
    assert document.dict() == utils.get_expected("script_pipeline_unstructured_form")


@pytest.mark.skipif(utils.skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_pubmed_xml():
    document = pipeline_pubmed_xml.ingest(
        1, -1, ["28508702[PMID]"], "", "", False
    ).dict()
    expected = utils.get_expected("script_pipeline_pubmed_xml")

    # We can't compare dates as it's determined in runtime.
    del document["context"]["pubmed_source_create_xml_collection_document"]["timestamp"]

    assert document["content"][0]["content"] != ""
    del document["content"][0]["content"]

    assert document == expected


@pytest.mark.skipif(utils.skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_pubmed_text():
    document = pipeline_pubmed_text.ingest(
        1, -1, ["28508702[PMID]"], "", "", False
    ).dict()
    expected = utils.get_expected("script_pipeline_pubmed_text")

    # We can't compare dates as it's determined in runtime.
    del document["context"]["pubmed_source_create_text_collection_document"][
        "timestamp"
    ]

    assert document["content"][0]["content"] != ""
    del document["content"][0]["content"]

    assert document == expected


@pytest.mark.skipif(utils.skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_pubmed_publication():
    document = pipeline_pubmed_publication.ingest(
        1, -1, ["28508702[PMID]"], False, "", ""
    ).dict()
    expected = utils.get_expected("script_pipeline_pubmed_publication")

    # We can't compare dates as it's determined in runtime.
    del document["context"]["pubmed_source_create_publication_collection_document"][
        "timestamp"
    ]
    del document["content"][0]["content"]

    assert document["content"][0]["abstract"] != ""
    del document["content"][0]["abstract"]

    assert document == expected


def test_pipeline_rss():
    # test that the plugin transformer is available
    pipeline_rss.generate_pipeline()


@pytest.mark.skipif(utils.skip_reddit, reason="INGESTUM_REDDIT_* variables not found")
def test_pipeline_reddit_form():
    document = pipeline_reddit_form.ingest("Sorcero", "all", "hot", 2)
    assert len(document.dict()["content"]) > 0


@pytest.mark.skipif(utils.skip_reddit, reason="INGESTUM_REDDIT_* variables not found")
def test_pipeline_reddit_publication():
    document = pipeline_reddit_publication.ingest("Sorcero", "all", "hot", 2)
    assert len(document.dict()["content"]) > 0


@pytest.mark.skipif(utils.skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_litcovid_publication():
    document = pipeline_litcovid_publication.ingest(
        "pmid:32870481", 1, -1, "score desc", [""], False, "", ""
    ).dict()
    expected = utils.get_expected("script_pipeline_litcovid_publication")

    # We can't compare dates as it's determined in runtime.
    del document["context"]["litcovid_source_create_publication_collection_document"][
        "timestamp"
    ]
    del document["content"][0]["abstract"]

    assert document == expected


@pytest.mark.skipif(utils.skip_biorxiv, reason="INGESTUM_BIORXIV_* variables not found")
def test_pipeline_biorxiv_publication():
    document = pipeline_biorxiv_publication.ingest(
        1, -1, "2021.07.28.453844", "biorxiv", False, "", ""
    ).dict()
    expected = utils.get_expected("script_pipeline_biorxiv_publication")

    # We can't compare dates as it's determined in runtime.
    del document["content"][0]["abstract"]
    del document["content"][0]["content"]
    del document["context"]["biorxiv_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document == expected


@pytest.mark.skipif(
    utils.skip_europepmc, reason="INGESTUM_EUROPEPMC_* variables not found"
)
def test_pipeline_europepmc_publication():
    document = pipeline_europepmc_publication.ingest(
        "34550700", 1, -1, "", "", False
    ).dict()
    expected = utils.get_expected("script_pipeline_europepmc_publication")

    del document["content"][0]["abstract"]
    del document["content"][0]["content"]
    # We can't compare dates as it's determined in runtime.
    del document["context"]["europepmc_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document == expected


def test_pipeline_pptx():
    document = pipeline_pptx.ingest(PPTX_data, 1, 3, None)
    assert document.dict() == utils.get_expected("script_pipeline_pptx")
