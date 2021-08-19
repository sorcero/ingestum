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


import inspect
import logging
import os
from typing import Callable, Literal, List, Union

from pydantic import BaseModel

from .. import utils


__logger__ = logging.getLogger("sorcero.ingestion.services")

__script__ = os.path.basename(__file__).replace(".py", "")

WORKER_DEFAULT = "legacy"


class BaseWorker(BaseModel):

    type: Literal[__script__] = __script__

    def _run(self, fn: Callable) -> List:
        PRINT_RUN_TIME = os.environ.get("INGESTUM_WORKER_LOG_TIME", 0)

        trigger_stack = inspect.stack()[2]
        trigger_file = trigger_stack[1]
        trigger_file = trigger_file[trigger_file.find("ingestum") :]
        trigger_func = trigger_stack[3]

        _, output = utils.calculate_runtime(
            fn,
            print_time=(True if PRINT_RUN_TIME == "1" else False),
            label=f"(run time) {trigger_file} {trigger_func}",
        )

        return output

    def run(self, operand_list, operator_fn: Callable, *args, **kwargs):
        raise NotImplementedError


def get_active_worker() -> BaseWorker:
    """
    Returns the selected worker class to use to process Map-like operations on lists.

    :return: Ingestum Worker instance
    :rtype: workers.base.BaseWorker
    """

    WORKER = os.environ.get("INGESTUM_WORKER", WORKER_DEFAULT)

    class Parser(BaseModel):
        worker: Union[tuple(utils.find_subclasses(BaseWorker))]

    try:
        worker = Parser(worker={"type": WORKER}).worker
    except:
        worker = Parser(worker={"type": WORKER_DEFAULT}).worker
        __logger__.debug(
            "defaulting to worker", extra={"props": {"worker": worker.type}}
        )

    return worker
