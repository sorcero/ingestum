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
import pytest

from ingestum import engine
from ingestum import manifests
from ingestum import pipelines
from ingestum import documents

from tests import utils


destinations = None


def setup_module():
    global destinations

    destinations = tempfile.TemporaryDirectory()


def teardown_module():
    destinations.cleanup()


def run_pipeline(pipeline, source):
    results, *_ = engine.run(
        manifest=manifests.Base(sources=[source]),
        pipelines=[pipeline],
        pipelines_dir=None,
        artifacts_dir=None,
        workspace_dir=None,
    )

    return results[0]


def test_pipeline_audio():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_audio.json")
    source = manifests.sources.Audio(
        id="",
        pipeline=pipeline.name,
        location=manifests.sources.locations.Local(
            path="tests/data/test.wav",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_audio")


def test_pipeline_csv():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_csv.json")
    source = manifests.sources.CSV(
        id="",
        pipeline=pipeline.name,
        location=manifests.sources.locations.Local(
            path="tests/data/test.csv",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_csv")


def test_pipeline_html():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_html.json")
    source = manifests.sources.HTML(
        id="",
        pipeline=pipeline.name,
        target="body",
        location=manifests.sources.locations.Local(
            path="tests/data/image.html",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_html")


def test_pipeline_image():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_image.json")
    source = manifests.sources.Image(
        id="",
        pipeline=pipeline.name,
        location=manifests.sources.locations.Local(
            path="tests/data/test.jpg",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
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
        location=manifests.sources.locations.Local(
            path="tests/data/test.pdf",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_pdf")


@pytest.mark.skipif(utils.skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_pdf_publication():
    pipeline = pipelines.Base.parse_file(
        "tests/pipelines/pipeline_pdf_publication.json"
    )
    source = manifests.sources.PDF(
        id="",
        pipeline=pipeline.name,
        location=manifests.sources.locations.Local(
            path="tests/data/test_pdf_publication.pdf"
        ),
        destination=manifests.sources.destinations.Local(directory=destinations.name),
    )
    document = run_pipeline(pipeline, source).dict()

    del document["abstract"]
    del document["content"]

    assert document == utils.get_expected("pipeline_pdf_publication")


def test_pipeline_pdf_no_pages():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_pdf.json")
    source = manifests.sources.PDF(
        id="",
        pipeline=pipeline.name,
        location=manifests.sources.locations.Local(
            path="tests/data/test.pdf",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
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
        location=manifests.sources.locations.Local(
            path="tests/data/test.pdf",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_ocr")


def test_pipeline_pdf_hybrid():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_pdf_hybrid.json")
    source = manifests.sources.PDF(
        id="",
        pipeline=pipeline.name,
        first_page=1,
        last_page=1,
        location=manifests.sources.locations.Local(
            path="tests/data/hybrid.pdf",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_pdf_hybrid")


def test_pipeline_text():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_text.json")
    source = manifests.sources.Text(
        id="",
        pipeline=pipeline.name,
        location=manifests.sources.locations.Local(
            path="tests/data/test.txt",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_text")


def test_pipeline_xls():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_xls.json")
    source = manifests.sources.XLS(
        id="",
        pipeline=pipeline.name,
        location=manifests.sources.locations.Local(
            path="tests/data/test.xlsx",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_xls")


def test_pipeline_xml():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_xml.json")
    source = manifests.sources.XML(
        id="",
        pipeline=pipeline.name,
        location=manifests.sources.locations.Local(
            path="tests/data/test.xml",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_xml")


def test_pipeline_docx():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_docx.json")
    source = manifests.sources.DOCX(
        id="",
        pipeline=pipeline.name,
        location=manifests.sources.locations.Local(
            path="tests/data/test.docx",
        ),
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert document.dict() == utils.get_expected("pipeline_docx")


@pytest.mark.skipif(utils.skip_reddit, reason="INGESTUM_REDDIT_* variables not found")
def test_pipeline_reddit_form():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_reddit_form.json")
    source = manifests.sources.Reddit(
        id="",
        pipeline=pipeline.name,
        search="python",
        subreddit="learnpython",
        sort="relevance",
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert len(document.content) > 0
    assert isinstance(document.content[0], documents.Form)


@pytest.mark.skipif(utils.skip_reddit, reason="INGESTUM_REDDIT_* variables not found")
def test_pipeline_reddit_publication():
    pipeline = pipelines.Base.parse_file(
        "tests/pipelines/pipeline_reddit_publication.json"
    )
    source = manifests.sources.Reddit(
        id="",
        pipeline=pipeline.name,
        search="python",
        subreddit="learnpython",
        sort="relevance",
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert len(document.content) > 0
    assert isinstance(document.content[0], documents.Publication)


def test_pipeline_rss():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_rss.json")
    source = manifests.sources.RSS(
        id="",
        pipeline=pipeline.name,
        location=manifests.sources.locations.Test(
            url="https://blogs.gnome.org/tchx84/feed/",
        ),
        destination=manifests.sources.destinations.Test(),
    )
    # test that all the plugin components can be de-serialized and can run
    run_pipeline(pipeline, source)


@pytest.mark.skipif(utils.skip_twitter, reason="INGESTUM_TWITTER_* variables not found")
def test_pipeline_twitter_form():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_twitter_form.json")
    source = manifests.sources.Twitter(
        id="",
        pipeline=pipeline.name,
        search="python",
        count=10,
        sort="recent",
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert len(document.content) > 0
    assert isinstance(document.content[0], documents.Form)


@pytest.mark.skipif(utils.skip_twitter, reason="INGESTUM_TWITTER_* variables not found")
def test_pipeline_twitter_publication():
    pipeline = pipelines.Base.parse_file(
        "tests/pipelines/pipeline_twitter_publication.json"
    )
    source = manifests.sources.Twitter(
        id="",
        pipeline=pipeline.name,
        search="python",
        count=10,
        sort="recent",
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert len(document.content) > 0
    assert isinstance(document.content[0], documents.Publication)


@pytest.mark.skipif(utils.skip_email, reason="INGESTUM_EMAIL_* variables not found")
def test_pipeline_email():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_email.json")
    source = manifests.sources.Email(
        id="",
        pipeline=pipeline.name,
        hours=24,
        sender="foo@bar.test",
        subject="foo",
        body="bar",
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source)

    assert len(document.content) == 0


@pytest.mark.skipif(utils.skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_pubmed_text():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_pubmed_text.json")
    source = manifests.sources.PubMed(
        id="",
        pipeline=pipeline.name,
        terms=["fake", "search", "term"],
        articles=10,
        hours=24,
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source).dict()

    del document["context"]["pubmed_source_create_text_collection_document"][
        "timestamp"
    ]

    assert document == utils.get_expected("pipeline_pubmed_text")


@pytest.mark.skipif(utils.skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_pubmed_xml():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_pubmed_xml.json")
    source = manifests.sources.PubMed(
        id="",
        pipeline=pipeline.name,
        terms=["fake", "search", "term"],
        articles=10,
        hours=24,
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source).dict()

    del document["context"]["pubmed_source_create_xml_collection_document"]["timestamp"]

    assert document == utils.get_expected("pipeline_pubmed_xml")


@pytest.mark.skipif(utils.skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_pubmed_publication():
    pipeline = pipelines.Base.parse_file(
        "tests/pipelines/pipeline_pubmed_publication.json"
    )
    source = manifests.sources.PubMed(
        id="",
        pipeline=pipeline.name,
        terms=["fake", "search", "term"],
        articles=10,
        hours=24,
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source).dict()

    del document["context"]["pubmed_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document == utils.get_expected("pipeline_pubmed_publication")


@pytest.mark.skipif(
    utils.skip_proquest, reason="INGESTUM_PROQUEST_* variables not found"
)
def test_pipeline_proquest_xml():
    pipeline = pipelines.Base.parse_file("tests/pipelines/pipeline_proquest_xml.json")
    source = manifests.sources.ProQuest(
        id="",
        pipeline=pipeline.name,
        query="noquery",
        databases=["nodatabase"],
        articles=1,
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source).dict()

    del document["context"]["proquest_source_create_xml_collection_document"][
        "timestamp"
    ]

    assert document == utils.get_expected("pipeline_proquest_xml")


@pytest.mark.skipif(
    utils.skip_proquest, reason="INGESTUM_PROQUEST_* variables not found"
)
def test_pipeline_proquest_publication():
    pipeline = pipelines.Base.parse_file(
        "tests/pipelines/pipeline_proquest_publication.json"
    )
    source = manifests.sources.ProQuest(
        id="",
        pipeline=pipeline.name,
        query="noquery",
        databases=["nodatabase"],
        articles=1,
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source).dict()

    del document["context"]["proquest_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document == utils.get_expected("pipeline_proquest_publication")


@pytest.mark.skipif(utils.skip_pubmed, reason="INGESTUM_PUBMED_* variables not found")
def test_pipeline_litcovid_publication():
    pipeline = pipelines.Base.parse_file(
        "tests/pipelines/pipeline_litcovid_publication.json"
    )
    source = manifests.sources.LitCovid(
        id="",
        pipeline=pipeline.name,
        query_string="countries:Test",
        articles=10,
        hours=24,
        sort="score desc",
        terms=["fake", "search", "term"],
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source).dict()

    del document["context"]["litcovid_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document == utils.get_expected("pipeline_litcovid_publication")


@pytest.mark.skipif(utils.skip_biorxiv, reason="INGESTUM_BIORXIV_* variables not found")
def test_pipeline_biorxiv_publication():
    pipeline = pipelines.Base.parse_file(
        "tests/pipelines/pipeline_biorxiv_publication.json"
    )
    source = manifests.sources.Biorxiv(
        id="",
        pipeline=pipeline.name,
        articles=1,
        hours=-1,
        repo="biorxiv",
        query="2021.07.28.453844",
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source).dict()

    del document["content"][0]["abstract"]
    del document["content"][0]["content"]
    del document["context"]["biorxiv_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document == utils.get_expected("pipeline_biorxiv_publication")


@pytest.mark.skipif(
    utils.skip_europepmc, reason="INGESTUM_EUROPEPMC_* variables not found"
)
def test_pipeline_europepmc_publication():
    pipeline = pipelines.Base.parse_file(
        "tests/pipelines/pipeline_europepmc_publication.json"
    )
    source = manifests.sources.EuropePMC(
        id="",
        pipeline=pipeline.name,
        query="34550700",
        articles=1,
        hours=-1,
        from_date="",
        to_date="",
        destination=manifests.sources.destinations.Local(
            directory=destinations.name,
        ),
    )
    document = run_pipeline(pipeline, source).dict()

    del document["content"][0]["abstract"]
    del document["context"]["europepmc_source_create_publication_collection_document"][
        "timestamp"
    ]
    del document["content"][0]["content"]

    assert document == utils.get_expected("pipeline_europepmc_publication")
