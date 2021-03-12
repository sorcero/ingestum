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


import os
import json
import unittest
import tempfile

from ingestum import engine
from ingestum import manifests
from ingestum import pipelines


class PipelinesTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.workspace = tempfile.TemporaryDirectory()

    def tearDown(self):
        super().tearDown()
        self.workspace.cleanup()

    def run_pipeline(self, pipeline, source):
        results = engine.run(
            manifest=manifests.Base(sources=[source]),
            pipelines=[pipeline],
            pipelines_dir=None,
            artifacts_dir=None,
            workspace_dir=self.workspace.name,
        )

        return results[0]

    def get_expected(self, script):
        filepath = os.path.join("tests/output/", script + ".json")
        with open(filepath, "r") as f:
            expected = json.loads(f.read())
        return expected

    def test_pipeline_audio(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_audio.json")
        source = manifests.sources.Audio(
            id="", pipeline=pipeline.name, url="file://tests/data/test.wav"
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_audio"))

    def test_pipeline_csv(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_csv.json")
        source = manifests.sources.CSV(
            id="", pipeline=pipeline.name, url="file://tests/data/test.csv"
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_csv"))

    def test_pipeline_html(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_html.json")
        source = manifests.sources.HTML(
            id="",
            pipeline=pipeline.name,
            target="body",
            url="file://tests/data/image.html",
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_html"))

    def test_pipeline_image(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_image.json")
        source = manifests.sources.Image(
            id="", pipeline=pipeline.name, url="file://tests/data/test.jpg"
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_image"))

    def test_pipeline_pdf(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_pdf.json")
        source = manifests.sources.PDF(
            id="",
            pipeline=pipeline.name,
            first_page=1,
            last_page=3,
            url="file://tests/data/test.pdf",
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_pdf"))

    def test_pipeline_pdf_no_pages(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_pdf.json")
        source = manifests.sources.PDF(
            id="",
            pipeline=pipeline.name,
            url="file://tests/data/test.pdf",
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_pdf"))

    def test_pipeline_ocr(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_ocr.json")
        source = manifests.sources.PDF(
            id="",
            pipeline=pipeline.name,
            first_page=1,
            last_page=3,
            url="file://tests/data/test.pdf",
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_ocr"))

    def test_pipeline_text(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_text.json")
        source = manifests.sources.Text(
            id="", pipeline=pipeline.name, url="file://tests/data/test.txt"
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_text"))

    def test_pipeline_xls(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_excel.json")
        source = manifests.sources.XLS(
            id="", pipeline=pipeline.name, url="file://tests/data/test.xlsx"
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_xls"))

    def test_pipeline_xml(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_xml.json")
        source = manifests.sources.XML(
            id="", pipeline=pipeline.name, url="file://tests/data/test.xml"
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_xml"))

    def test_pipeline_docx(self):
        pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_docx.json")
        source = manifests.sources.DOCX(
            id="", pipeline=pipeline.name, url="file://tests/data/test.docx"
        )
        document = self.run_pipeline(pipeline, source)

        self.assertEqual(document.dict(), self.get_expected("pipeline_docx"))


if __name__ == "__main__":
    unittest.main()
