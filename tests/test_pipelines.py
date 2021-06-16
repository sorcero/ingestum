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


import tempfile

from ingestum import engine
from ingestum import manifests
from ingestum import pipelines

from tests import utils


def setup_module():
    global workspace

    workspace = tempfile.TemporaryDirectory()


def teardown_module():
    workspace.cleanup()


def run_pipeline(pipeline, source):
    results, _ = engine.run(
        manifest=manifests.Base(sources=[source]),
        pipelines=[pipeline],
        pipelines_dir=None,
        artifacts_dir=None,
        workspace_dir=workspace.name,
    )

    return results[0]


def test_pipeline_audio():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_audio.json")
    source = manifests.sources.Audio(
        id="", pipeline=pipeline.name, url="file://tests/data/test.wav"
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_audio")


def test_pipeline_csv():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_csv.json")
    source = manifests.sources.CSV(
        id="", pipeline=pipeline.name, url="file://tests/data/test.csv"
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_csv")


def test_pipeline_html():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_html.json")
    source = manifests.sources.HTML(
        id="",
        pipeline=pipeline.name,
        target="body",
        url="file://tests/data/image.html",
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_html")


def test_pipeline_image():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_image.json")
    source = manifests.sources.Image(
        id="", pipeline=pipeline.name, url="file://tests/data/test.jpg"
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_image")


def test_pipeline_pdf():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_pdf.json")
    source = manifests.sources.PDF(
        id="",
        pipeline=pipeline.name,
        first_page=1,
        last_page=3,
        url="file://tests/data/test.pdf",
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_pdf")


def test_pipeline_pdf_no_pages():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_pdf.json")
    source = manifests.sources.PDF(
        id="",
        pipeline=pipeline.name,
        url="file://tests/data/test.pdf",
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_pdf")


def test_pipeline_ocr():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_ocr.json")
    source = manifests.sources.PDF(
        id="",
        pipeline=pipeline.name,
        first_page=1,
        last_page=3,
        url="file://tests/data/test.pdf",
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_ocr")


def test_pipeline_text():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_text.json")
    source = manifests.sources.Text(
        id="", pipeline=pipeline.name, url="file://tests/data/test.txt"
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_text")


def test_pipeline_xls():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_excel.json")
    source = manifests.sources.XLS(
        id="", pipeline=pipeline.name, url="file://tests/data/test.xlsx"
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_xls")


def test_pipeline_xml():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_xml.json")
    source = manifests.sources.XML(
        id="", pipeline=pipeline.name, url="file://tests/data/test.xml"
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_xml")


def test_pipeline_docx():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_docx.json")
    source = manifests.sources.DOCX(
        id="", pipeline=pipeline.name, url="file://tests/data/test.docx"
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_docx")