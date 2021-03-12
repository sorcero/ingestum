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


from . import base
from . import all_attribute_matches_regexp
from . import passage_has_tag_prefix
from . import passage_has_content_prefix
from . import tabular_has_fewer_columns
from . import tabular_row_matches_regexp
from . import tabular_row_has_n_values
from . import tabular_row_has_empty_front_cells

# XXX these import other conditionals
from . import tabular_row_matches
from . import all_and
from . import all_or
from . import all_negate

BaseConditional = base.BaseConditional

AllNegate = all_negate.Conditional
AllAnd = all_and.Conditional
AllOr = all_or.Conditional
AllAttributeMatchesRegexp = all_attribute_matches_regexp.Conditional

PassageHasTagPrefix = passage_has_tag_prefix.Conditional
PassageHasContentPrefix = passage_has_content_prefix.Conditional

TabularHasFewerColumns = tabular_has_fewer_columns.Conditional
TabularRowMatchesRegexp = tabular_row_matches_regexp.Conditional
TabularRowHasNValues = tabular_row_has_n_values.Conditional
TabularRowHasEmptyFrontCells = tabular_row_has_empty_front_cells.Conditional
TabularRowMatches = tabular_row_matches.Conditional
