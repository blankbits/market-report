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

import matplotlib as mpl
import numpy as np

def format_x_ticks_as_dates(plot):
    plot.xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y-%m-%d'))
    plot.get_xaxis().get_label().set_visible(False)
    return plot

def format_y_ticks_as_percents(plot):
    y_ticks = plot.get_yticks()
    # plot.set_yticklabels([
    #     '{:3.1f}%'.format(tick * 100.0) for tick in y_ticks])
    plot.set_yticklabels(get_percent_strings(y_ticks))
    return plot

def format_y_ticks_as_dollars(plot):
    y_ticks = plot.get_yticks()
    plot.set_yticklabels(['${:,.0f}'.format(tick) for tick in y_ticks])
    return plot

def format_legend(plot, text_color):
    legend = plot.legend(loc='upper left', borderaxespad=0)
    for text in legend.get_texts():
        text.set_color(text_color)
    return plot

def add_bar_labels(plot, labels, text_color):
    rects = plot.patches
    for rect, label in zip(rects, labels):
        height = rect.get_height() * (-1.0 if rect.get_y() < 0 else 1.0)
        vert_align = 'top' if rect.get_y() < 0 else 'bottom'
        plot.text(rect.get_x() + rect.get_width() * .5, height, (
            label), ha='center', va=vert_align, color=text_color)
    return plot

def get_percent_strings(values):
    return ['{:3.1f}%'.format(x * 100.0) for x in values]

def get_conditional_colors(values, alpha):
    # Color positive values green, negative values red, and adjust intensity by
    # relative magnitude.
    max_abs_value = max(np.abs(values))
    colors = [(0.0, 0.0, 0.0, 0.0)] * len(values)
    for i, item in enumerate(values):
        intensity = .75 * (1.0 - (np.abs(item) / max_abs_value))
        colors[i] = (1.0, intensity, intensity, alpha) if item < 0 else (
            intensity, 1.0, intensity, alpha)
    return colors
