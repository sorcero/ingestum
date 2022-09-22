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


from pydantic import BaseModel, ValidationError
from pydantic.class_validators import ROOT_KEY
from pydantic.error_wrappers import ErrorWrapper
from typing import List, Union
from typing_extensions import Literal

from . import sources
from .. import transformers
from ..utils import find_subclasses


class Pipe(BaseModel):
    """
    :param name: Pipe name
    :type name: str
    :param sources: List of sources to be ingested
    :type sources: List[Union[tuple(find_subclasses(sources.Base))]]
    :param steps: List of transformers in the order in which they will be applied
    :type steps: List[Union[tuple(find_subclasses(transformers.base.BaseTransformer))]]
    """

    type: Literal["base"] = "base"
    name: str = ""
    sources: List[Union[tuple(find_subclasses(sources.Base))]]
    steps: List[Union[tuple(find_subclasses(transformers.base.BaseTransformer))]]


class Pipeline(BaseModel):
    """
    :param name: Pipeline name
    :type name: str
    :param pipes: Collection of pipes
    :type pipes: List[Pipe]
    """

    type: Literal["base"] = "base"
    name: str = ""
    pipes: List[Pipe]

    def __init__(self, **kargs):
        # XXX silence unuseful backtrace until pydantic discriminators lands
        try:
            super().__init__(**kargs)
        except ValidationError:
            e = TypeError(
                "Pipeline is not valid, please double check transformers and arguments"
            )
            raise ValidationError(
                [ErrorWrapper(e, loc=ROOT_KEY)], self.__class__
            ) from None

    def _treat_sources(
        self, output_dir, manifest_source, documents, pipe_sources, cache_dir
    ):  # noqa: E501
        _sources = []

        for source in pipe_sources:
            if isinstance(source, sources.Pipe):
                _sources.append(documents.get(source.name))
            elif isinstance(source, sources.Manifest):
                _sources.append(
                    manifest_source.get_source(
                        output_dir=output_dir, cache_dir=cache_dir
                    )
                )
            elif isinstance(source, sources.Nothing):
                _sources.append(None)

        return _sources

    def run(self, output_dir, manifest_source, cache_dir=None):
        documents = {}
        document = None

        for pipe in self.pipes:
            for index, transformer in enumerate(pipe.steps):
                if index == 0:
                    document = transformer.transform(
                        *self._treat_sources(
                            output_dir,
                            manifest_source,
                            documents,
                            pipe.sources,
                            cache_dir,
                        )
                    )
                else:
                    document = transformer.transform(document)
            documents[pipe.name] = document

        return document
