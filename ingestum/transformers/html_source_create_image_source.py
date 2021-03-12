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


import os
import uuid
import pathlib
import asyncio

from pyppeteer import launcher
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms an HTML source into a Image source.
    """

    class ArgumentsModel(BaseModel):
        directory: str
        url: Optional[str]
        full: Optional[bool] = True

    class InputsModel(BaseModel):
        source: sources.HTML

    class OutputsModel(BaseModel):
        source: sources.Image

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    async def extract(self, url, path):
        browser = await launcher.launch(
            {"args": ["--no-sandbox", "--allow-file-access-from-files"]}
        )
        page = await browser.newPage()
        await page.goto(url)
        await page.screenshot(path=path, fullPage=self.arguments.full)
        await browser.close()

    def transform(self, source):
        super().transform(source=source)

        url = self.arguments.url
        if url is None:
            url = f"file://{source.path}"

        pathlib.Path(self.arguments.directory).mkdir(parents=True, exist_ok=True)
        path = os.path.join(self.arguments.directory, f"{str(uuid.uuid4())}.png")

        asyncio.get_event_loop().run_until_complete(self.extract(url, path))

        output_source = sources.Image(path=path)

        return output_source
