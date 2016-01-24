import numpy as np
import pandas as pd

def get_histogram(series, bins, bins_decimals=0, bins_is_percent=False,
                  block_count=100):
    histogram = ''
    buckets = series.groupby(pd.cut(series, bins)).count()
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
    column = ''
    label_len = len(max(list(series.axes[0]), key=len))
    value_len = len(str(max([str(x) for x in np.round(
        list(abs(series.values)), decimals)], key=len))) + 1
    format_str = ('%-' + str(label_len) + 's  %+' + str(value_len) + '.' +
                  str(decimals) + 'f' + ('%%\n' if is_percent else '\n'))
    for key, value in series.iteritems():
        column += format_str % (key, value)
    return column

def join_lines(columns, separator=''):
    split_columns = [x.split('\n') for x in columns]
    widths = [max(x) for x in [[len(y) for y in z] for z in split_columns]]
    result = ''
    for i in range(max([len(x) for x in split_columns])):
        for j, column in enumerate(split_columns):
            result += ('%-' + str(widths[j] + len(separator)) + 's') % (
                '' if i > len(column) - 1 else column[i])

        result += '\n'
    return result
