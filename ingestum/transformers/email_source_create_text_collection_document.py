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
import email
import imaplib
import datetime

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .base import BaseTransformer
from .. import sources
from .. import documents

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Extracts `Emails` received in the last hours from sender and returns a
    collection of `Text` documents for each email.

    :param hours: Hours to look back
    :type hours: int
    :param sender: Sender of email
    :type sender: str
    :param subject: Keywords in subject
    :type subject: str
    :param body: Keywords in body
    :type body: str
    """

    class ArgumentsModel(BaseModel):
        hours: Optional[int] = None
        sender: Optional[str] = None
        subject: Optional[str] = None
        body: Optional[str] = None

    class InputsModel(BaseModel):
        source: sources.Email

    class OutputsModel(BaseModel):
        document: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def contentize(self, message, content_type):
        contents = []

        content = None
        if message.is_multipart():
            payload = message.get_payload()
            for sub_message in payload:
                if sub_message.get_content_type() == content_type:
                    content = sub_message.get_payload()
                    break

        # if we don't find the proper type get what we can.
        if content is None:
            content = message.get_payload()

        # forwarded emails are not multipart but a split in multiple parts.
        if isinstance(content, list):
            for message in content:
                contents += self.contentize(message, content_type)
        else:
            contents.append(content)

        return contents

    def extract(self, source, content_type="text/plain"):
        documents_ = []

        server = imaplib.IMAP4_SSL(host=source.host, port=source.port)
        server.login(source.user, source.password)
        server.select(readonly=True)

        args = []
        if self.arguments.hours:
            delta = datetime.timedelta(hours=self.arguments.hours)
            date = datetime.datetime.now() - delta
            date = date.strftime("%d-%b-%Y")
            args.append(f"(SENTSINCE {date})")
        if self.arguments.sender:
            args.append(f"(FROM {self.arguments.sender})")
        if self.arguments.subject:
            args.append(f'SUBJECT "{self.arguments.subject}"')
        if self.arguments.body:
            args.append(f'BODY "{self.arguments.body}"')

        _, message_numbers_raw = server.search(None, *args)
        for message_number in message_numbers_raw[0].split():
            _, msg = server.fetch(message_number, "(RFC822)")
            message = email.message_from_bytes(msg[0][1])

            contents = self.contentize(message, content_type)
            if content_type == "text/plain":
                for content in contents:
                    document = documents.Text.new_from(None, content=content)
                    documents_.append(document)
            if content_type == "text/html":
                for content in contents:
                    document = documents.HTML.new_from(None, content=content)
                    documents_.append(document)

        return documents_

    def transform(self, source: sources.Email) -> documents.Collection:
        super().transform(source=source)

        content = self.extract(source)

        return documents.Collection.new_from(source, content=content)
