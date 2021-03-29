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
import json
import unittest

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


class ScriptsTestCase(unittest.TestCase):

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

    def get_expected(self, script):
        filepath = os.path.join("tests/output/", script + ".json")
        with open(filepath, "r") as f:
            expected = json.loads(f.read())
        return expected

    @unittest.skipIf(skip_twitter, "INGESTUM_TWITTER_* variables not found")
    def test_pipeline_twitter(self):
        document = pipeline_twitter.ingest("Sorcero")
        self.assertTrue(len(document.dict()["content"]) > 0)

    def test_pipeline_text(self):
        document = pipeline_text.ingest("file://%s" % self.Text_data)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_text"))

    def test_pipeline_xml(self):
        document = pipeline_xml.ingest("file://%s" % self.XML_data)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_xml"))

    def test_pipeline_csv(self):
        document = pipeline_csv.ingest("file://%s" % self.CSV_data)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_csv"))

    def test_pipeline_excel(self):
        document = pipeline_excel.ingest("file://%s" % self.XLS_data)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_xls"))

    def test_pipeline_html(self):
        document = pipeline_html.ingest("file://%s" % self.HTML_data, "body")
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_html"))

    def test_pipeline_image(self):
        document = pipeline_image.ingest("file://%s" % self.Image_data)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_image"))

    def test_pipeline_ocr(self):
        document = pipeline_ocr.ingest("file://%s" % self.OCR_data, 1, 3)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_ocr"))

    def test_pipeline_pdf(self):
        document = pipeline_pdf.ingest("file://%s" % self.PDF_data, 1, 3)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_pdf"))

    def test_pipeline_pdf_no_pages(self):
        document = pipeline_pdf.ingest("file://%s" % self.PDF_data, None, None)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_pdf"))

    def test_pipeline_audio(self):
        document = pipeline_audio.ingest("file://%s" % self.Audio_data)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_audio"))

    def test_pipeline_annotation(self):
        document = pipeline_annotation.ingest("file://%s" % self.Annotation_data, 1, 1)
        self.assertEqual(
            document.dict(), self.get_expected("script_pipeline_annotation")
        )

    def test_pipeline_document(self):
        document = pipeline_document.ingest("file://%s" % self.Document_data)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_document"))

    @unittest.skipIf(skip_email, "INGESTUM_EMAIL_* variables not found")
    def test_pipeline_email(self):
        document = pipeline_email.ingest(24, "test@test.test", "subject", "body")
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_email"))

    @unittest.skipIf(skip_proquest, "INGESTUM_PROQUEST_* variables not found")
    def test_pipeline_proquest(self):
        document = pipeline_proquest.ingest("noquery", ["nodatabase"])
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_proquest"))

    def test_pipeline_docx(self):
        document = pipeline_docx.ingest("file://%s" % self.DOCX_data)
        self.assertEqual(document.dict(), self.get_expected("script_pipeline_docx"))

    def test_pipeline_unstructured_form(self):
        document = pipeline_unstructured_form.ingest(
            "file://%s" % self.UForm_data, 1, 1
        )
        self.assertEqual(
            document.dict(), self.get_expected("script_pipeline_unstructured_form")
        )

    @unittest.skipIf(skip_pubmed, "INGESTUM_PUBMED_* variables not found")
    def test_pipeline_pubmed(self):
        # Test the xml and text versions of the Pubmed pipelines.
        document = pipeline_pubmed_xml.ingest(1, 24, ["fake", "search", "term"]).dict()
        expected = self.get_expected("script_pipeline_pubmed_xml")

        # We can't compare dates as it's determined in runtime.
        del document["context"]["pubmed_source_create_xml_collection_document"][
            "timestamp"
        ]

        del expected["context"]["pubmed_source_create_xml_collection_document"][
            "timestamp"
        ]

        document = pipeline_pubmed_text.ingest(1, 24, ["fake", "search", "term"]).dict()
        expected = self.get_expected("script_pipeline_pubmed_text")

        # We can't compare dates as it's determined in runtime.
        del document["context"]["pubmed_source_create_text_collection_document"][
            "timestamp"
        ]

        del expected["context"]["pubmed_source_create_text_collection_document"][
            "timestamp"
        ]

        self.assertEqual(document, expected)

    def test_pipeline_rss(self):
        # test that the plugin transformer is available
        pipeline_rss.generate_pipeline()


if __name__ == "__main__":
    unittest.main()
