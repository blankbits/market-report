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

"""
Contains utility functions for generating plots with matplotlib.
"""

import matplotlib as mpl
import numpy as np

def format_x_ticks_as_dates(plot):
    """Formats x ticks YYYY-MM-DD and removes the default 'Date' label.

    Args:
        plot: matplotlib.AxesSubplot object.
    """
    plot.xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y-%m-%d'))
    plot.get_xaxis().get_label().set_visible(False)
    return plot

def format_y_ticks_as_percents(plot):
    """Formats y ticks as nice-looking percents.

    Args:
        plot: matplotlib.AxesSubplot object.
    """
    y_ticks = plot.get_yticks()
    plot.set_yticklabels(get_percent_strings(y_ticks))
    return plot

def format_y_ticks_as_dollars(plot):
    """Formats y ticks as dollar values with commas and no decimals.

    Args:
        plot: matplotlib.AxesSubplot object.
    """
    y_ticks = plot.get_yticks()
    plot.set_yticklabels(['${:,.0f}'.format(tick) for tick in y_ticks])
    return plot

def format_legend(plot, text_color):
    """Moves legend to the upper left of the plot area with no padding, and sets
    the text color.

    Args:
        plot: matplotlib.AxesSubplot object.
        text_color: matplotlib RGB color tuple.
    """
    legend = plot.legend(loc='upper left', borderaxespad=0)
    for text in legend.get_texts():
        text.set_color(text_color)
    return plot

def add_bar_labels(plot, labels, text_color):
    """Draws text labels just above (below) bars in the plot for positive
    (negative) values.

    Args:
        plot: matplotlib.AxesSubplot object.
        labels: List of strings corresponding to bars in plot.
        text_color: matplotlib RGB color tuple.
    """
    rects = plot.patches
    for rect, label in zip(rects, labels):
        height = rect.get_height() * (-1.0 if rect.get_y() < 0 else 1.0)
        vert_align = 'top' if rect.get_y() < 0 else 'bottom'
        plot.text(rect.get_x() + rect.get_width() * .5, height, (
            label), ha='center', va=vert_align, color=text_color)
    return plot

def get_percent_strings(values):
    """Formats floating point values as percent strings with one decimal place
    e.g. '%99.9'.

    Args:
        values: List of floating point values.
    """
    return ['{:3.1f}%'.format(x * 100.0) for x in values]

def get_conditional_colors(values, alpha):
    """Generates colors with positive values green and negative values red.
    Intensity varies by relative magnitude.

    Args:
        values: List of floating point values.
        alpha: Degree of transparency in returned colors.
    """
    max_abs_value = max(np.abs(values))
    colors = [(0.0, 0.0, 0.0, 0.0)] * len(values)
    for i, item in enumerate(values):
        intensity = .75 * (1.0 - (np.abs(item) / max_abs_value))
        colors[i] = (1.0, intensity, intensity, alpha) if item < 0 else (
            intensity, 1.0, intensity, alpha)
    return colors
