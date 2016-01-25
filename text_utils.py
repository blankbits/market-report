# Copyright 2016 Peter Dymkar Brandt All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""This file contains util functions to assist in building text-based
visualizations of numeric data.
"""

import numpy as np
import pandas as pd

def get_histogram(series, bins, bins_decimals=0, bins_is_percent=False,
                  block_count=100):
    """Creates a text-based histogram.

    Args:
        series: pandas.Series of numeric values.
        bins: List of boundaries between bins in ascending order.
        bins_decimals: Number of decimals to use for bins in format string.
        bins_is_percent: Whether to print a '%' character for bins.
        block_count: Total number of block characters in histogram.
    """
    histogram = ''
    buckets = series.groupby(pd.cut(series, bins)).count()

    # Find the max string length for an individual bin value so that right
    # alignment works properly.
    max_bin_value_len = len(str(int(np.round(max(abs(bins)))))) + (
        (bins_decimals + 1) if bins_decimals > 0 else 0) + 1

    format_str = '  '.join(['%+' + str(max_bin_value_len) + '.' + str(
        bins_decimals) + ('f%%'if bins_is_percent else 'f')] * 2) + (
            '  %-' + str(len(str(buckets.max()))) + 'i  %s\n')
    for i in range(buckets.size):
        # Due to rounding exact number of blocks may vary.
        histogram += format_str % (bins[i], bins[i + 1], buckets[i], ''.join(
            [u'\u2588'] * np.round(block_count * buckets[i] / series.size)))
    return histogram

def get_column(series, decimals=1, is_percent=False):
    """Creates a text-based column with labels on the left and numeric values on
    the right.

    Args:
        series: pandas.Series of numeric values.
        decimals: Number of decimals to use in format string.
        is_percent: Whether to print a '%' character for values.
    """
    column = ''

    # Find max string length for labels and values so that right alignment works
    # properly.
    label_len = len(max(list(series.axes[0]), key=len))
    value_len = len(str(max([str(x) for x in np.round(
        list(abs(series.values)), decimals)], key=len))) + 1

    format_str = ('%-' + str(label_len) + 's  %+' + str(value_len) + '.' +
                  str(decimals) + 'f' + ('%%\n' if is_percent else '\n'))
    for key, value in series.iteritems():
        column += format_str % (key, value)
    return column

def join_lines(columns, separator=''):
    """Joins an arbitrary number of multi-line strings side-by-side splitting on
    the '\n' character. It pads the ends of lines with ' ' characters as needed
    to preserve alignment.

    Args:
        columns: List of multi-line strings to join.
        separator: Padding inserted between each column.
    """
    split_columns = [x.split('\n') for x in columns]

    # Max line width for each input column.
    widths = [max(x) for x in [[len(y) for y in z] for z in split_columns]]

    result = ''
    for i in range(max([len(x) for x in split_columns])):
        for j, column in enumerate(split_columns):
            result += ('%-' + str(widths[j] + len(separator)) + 's') % (
                '' if i > len(column) - 1 else column[i])

        result += '\n'
    return result
