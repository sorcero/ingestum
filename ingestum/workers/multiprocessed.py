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
import multiprocessing
import multiprocessing.pool
from typing import Callable, List, Literal

from .base import BaseWorker


__script__ = os.path.basename(__file__).replace(".py", "")


INGESTUM_WORKERS = os.environ.get(
    "INGESTUM_MULTIPROCESSING_DEGREE", str(multiprocessing.cpu_count())
)


class NoDaemonProcess(multiprocessing.Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, _):
        pass


class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess


def apply_args_and_kwargs(fn, operand, args, kwargs):
    return fn(operand, *args, **kwargs)


class WorkerPool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        kwargs["context"] = NoDaemonContext()
        super(WorkerPool, self).__init__(*args, **kwargs)

    def starmap_with_kwargs(self, fn, operand_list, args, kwargs):
        starmap_args = tuple(map(lambda x: tuple([fn, x, args, kwargs]), operand_list))

        return self.starmap(apply_args_and_kwargs, starmap_args)


class Worker(BaseWorker):

    type: Literal[__script__] = __script__

    def _split_and_run(self, operator_fn, operand_list, *args, **kwargs):
        pool = WorkerPool(int(INGESTUM_WORKERS))

        result = pool.starmap_with_kwargs(operator_fn, operand_list, args, kwargs)

        pool.close()
        pool.join()

        return result

    def run(self, operand_list, operator_fn: Callable, *args, **kwargs) -> List:
        return self._run(
            lambda: self._split_and_run(operator_fn, operand_list, *args, **kwargs)
        )
