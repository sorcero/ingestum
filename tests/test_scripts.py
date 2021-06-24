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
import pipeline_excel
import pipeline_html
import pipeline_image
import pipeline_ocr
import pipeline_pdf
import pipeline_text
import pipeline_twitter
import pipeline_xml
import pipeline_document
import pipeline_email
import pipeline_proquest
import pipeline_rss
import pipeline_docx
import pipeline_unstructured_form
import pipeline_pubmed_xml
import pipeline_pubmed_text
import pipeline_reddit

from tests import utils

skip_twitter = (
    os.environ.get("INGESTUM_TWITTER_CONSUMER_KEY") is None
    or os.environ.get("INGESTUM_TWITTER_CONSUMER_SECRET") is None
    or os.environ.get("INGESTUM_TWITTER_ACCESS_TOKEN") is None
    or os.environ.get("INGESTUM_TWITTER_ACCESS_SECRET") is None
)

skip_proquest = (
    os.environ.get("INGESTUM_PROQUEST_TOKEN") is None
    or os.environ.get("INGESTUM_PROQUEST_ENDPOINT") is None
)

skip_email = (
    os.environ.get("INGESTUM_EMAIL_HOST") is None
    or os.environ.get("INGESTUM_EMAIL_PORT") is None
    or os.environ.get("INGESTUM_EMAIL_USER") is None
    or os.environ.get("INGESTUM_EMAIL_PASSWORD") is None
)

skip_pubmed = (
    os.environ.get("INGESTUM_PUBMED_TOOL") is None
    or os.environ.get("INGESTUM_PUBMED_EMAIL") is None
)

skip_reddit = (
    os.environ.get("INGESTUM_REDDIT_CLIENT_ID") is None
    or os.environ.get("INGESTUM_REDDIT_CLIENT_ID") is None
)


Annotation_data = "tests/data/test.pdf"
Audio_data = "tests/data/test.wav"
CSV_data = "tests/data/test.csv"
XLS_data = "tests/data/test.xlsx"
HTML_data = "tests/data/test.html"
Image_data = "tests/data/test.jpg"
OCR_data = "tests/data/test.pdf"
PDF_data = "tests/data/test.pdf"
Text_data = "tests/data/test.txt"
XML_data = "tests/data/test.xml"
Document_data = "tests/output/script_pipeline_document.json"
DOCX_data = "tests/data/test.docx"
UForm_data = "tests/data/unstructured_form.pdf"


@pytest.mark.skipif(skip_twitter, reason="INGESTUM_TWITTER_* variables not found")
def test_pipeline_twitter():
    document = pipeline_twitter.ingest("Sorcero")
    assert len(document.dict()["content"]) > 0


def test_pipeline_text():
    document = pipeline_text.ingest("file://%s" % Text_data)
    assert document.dict() == utils.get_expected("script_pipeline_text")


def test_pipeline_xml():
    document = pipeline_xml.ingest("file://%s" % XML_data)
    assert document.dict() == utils.get_expected("script_pipeline_xml")


def test_pipeline_csv():
    document = pipeline_csv.ingest("file://%s" % CSV_data)
    assert document.dict() == utils.get_expected("script_pipeline_csv")


def test_pipeline_excel():
    document = pipeline_excel.ingest("file://%s" % XLS_data)
    assert document.dict() == utils.get_expected("script_pipeline_xls")


def test_pipeline_html():
    document = pipeline_html.ingest("file://%s" % HTML_data, "body")
    assert document.dict() == utils.get_expected("script_pipeline_html")


def test_pipeline_image():
    document = pipeline_image.ingest("file://%s" % Image_data)
    assert document.dict() == utils.get_expected("script_pipeline_image")


def test_pipeline_ocr():
    document = pipeline_ocr.ingest("file://%s" % OCR_data, 1, 3)
    assert document.dict() == utils.get_expected("script_pipeline_ocr")


def test_pipeline_pdf():
    document = pipeline_pdf.ingest("file://%s" % PDF_data, 1, 3)
    assert document.dict() == utils.get_expected("script_pipeline_pdf")


def test_pipeline_pdf_no_pages():
    document = pipeline_pdf.ingest("file://%s" % PDF_data, None, None)
    assert document.dict() == utils.get_expected("script_pipeline_pdf")


def test_pipeline_audio():
    document = pipeline_audio.ingest("file://%s" % Audio_data)
    assert document.dict() == utils.get_expected("script_pipeline_audio")


def test_pipeline_annotation():
    document = pipeline_annotation.ingest("file://%s" % Annotation_data, 1, 1)
    assert document.dict() == utils.get_expected("script_pipeline_annotation")


def test_pipeline_document():
    document = pipeline_document.ingest("file://%s" % Document_data)
    assert document.dict() == utils.get_expected("script_pipeline_document")


@pytest.mark.skipif(skip_email, reason="INGESTUM_EMAIL_* variables not found")
def test_pipeline_email():
    document = pipeline_email.ingest(24, "test@test.test", "subject", "body")
    assert document.dict() == utils.get_expected("script_pipeline_email")


@pytest.mark.skipif(skip_proquest, reason="INGESTUM_PROQUEST_* variables not found")
def test_pipeline_proquest():
    document = pipeline_proquest.ingest("noquery", ["nodatabase"])
    assert document.dict() == utils.get_expected("script_pipeline_proquest")


def test_pipeline_docx():
    document = pipeline_docx.ingest("file://%s" % DOCX_data)
    assert document.dict() == utils.get_expected("script_pipeline_docx")


def test_pipeline_unstructured_form():
    document = pipeline_unstructured_form.ingest("file://%s" % UForm_data, 1, 1)
    assert document.dict() == utils.get_expected("script_pipeline_unstructured_form")


@pytest.mark.skipif(skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_pubmed_xml():
    document = pipeline_pubmed_xml.ingest(10, 24, ["fake", "search", "term"]).dict()
    expected = utils.get_expected("script_pipeline_pubmed_xml")

    # We can't compare dates as it's determined in runtime.
    del document["context"]["pubmed_source_create_xml_collection_document"]["timestamp"]

    del expected["context"]["pubmed_source_create_xml_collection_document"]["timestamp"]

    assert document == expected


@pytest.mark.skipif(skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_pubmed_text():
    document = pipeline_pubmed_text.ingest(10, 24, ["fake", "search", "term"]).dict()
    expected = utils.get_expected("script_pipeline_pubmed_text")

    # We can't compare dates as it's determined in runtime.
    del document["context"]["pubmed_source_create_text_collection_document"][
        "timestamp"
    ]

    del expected["context"]["pubmed_source_create_text_collection_document"][
        "timestamp"
    ]

    assert document == expected


def test_pipeline_rss():
    # test that the plugin transformer is available
    pipeline_rss.generate_pipeline()


@pytest.mark.skipif(skip_reddit, reason="INGESTUM_REDDIT_* variables not found")
def test_pipeline_reddit():
    document = pipeline_reddit.ingest("Sorcero")
    assert len(document.dict()["content"]) > 0
