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
PortfolioReport generates visualizations of past performance of a portfolio of
financial instruments.

Example:
    # See historical_data documentation for more info.
    data = historical_data.HistoricalData(historical_data_config,
                                          tor_scraper_config)
    daily = data.get_daily()
    if daily is None:
        return
    print portfolio_report.PortfolioReport({
        'subject_format': 'Portfolio Report -- %s',
    }, daily).get_report()
"""

import sys

import matplotlib.pyplot as plt
import numpy as np

class PortfolioReport(object):
    """Contains all functionality for the portfolio_report module.
    """
    def __init__(self, portfolio_report_config, daily):
        """PortfolioReport must be initialized with args similar to those shown
        in the example at the top of this file.

        Args:
            portfolio_report_config: Determines the behavior of this instance.
            daily: pandas.DataFrame of prices of the same type returned by
                historical_data.get_daily(). Rows represent dates in ascending
                order, and columns represent financial instruments.
        """
        self._config = portfolio_report_config
        self._daily = daily

    def test_plot(self):
        #plt.style.use('ggplot')
        plt.style.use('fivethirtyeight')

        fig, axes = plt.subplots(ncols=2, nrows=2)
        ax1, ax2, ax3, ax4 = axes.ravel()

        # scatter plot (Note: `plt.scatter` doesn't use default colors)
        x, y = np.random.normal(size=(2, 200))
        ax1.plot(x, y, 'o')

        # sinusoidal lines with colors from default color cycle
        L = 2*np.pi
        x = np.linspace(0, L)
        ncolors = len(plt.rcParams['axes.color_cycle'])
        shift = np.linspace(0, L, ncolors, endpoint=False)
        for s in shift:
            ax2.plot(x, np.sin(x + s), '-')

        ax2.margins(0)

        # bar graphs
        x = np.arange(5)
        y1, y2 = np.random.randint(1, 25, size=(2, 5))
        width = 0.25
        ax3.bar(x, y1, width)
        ax3.bar(x + width, y2, width, color=plt.rcParams['axes.color_cycle'][0])
        ax3.set_xticks(x + width)
        ax3.set_xticklabels(['a', 'b', 'c', 'd', 'e'])

        # circles with colors from default color cycle
        for i, color in enumerate(plt.rcParams['axes.color_cycle']):
            xy = np.random.normal(size=2)
            ax4.add_patch(plt.Circle(xy, radius=0.3, color=color))

        ax4.axis('equal')
        ax4.margins(0)

        plt.show()

    def get_report(self):
        """Creates the entire report.
        """
        subject = self._config['subject_format'] % str(
            self._daily['adj_close'].index[-1].date())
        body = ''

        self.test_plot()

        return {'subject': subject, 'body': body}
