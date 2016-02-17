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

    def get_returns_bar_plot(self, offset):
        returns = ((self._daily['adj_close'].iloc[-1, :] - (
            self._daily['adj_close'].iloc[-(offset + 1), :])) / (
                self._daily['adj_close'].iloc[-(offset + 1), :])).sort_index()
        max_abs_return = max(np.abs(returns))

        # Color gains green, losses red, and adjust alpha by magnitude.
        colors = [(0.0, 0.0, 0.0)] * len(returns)
        for i, item in enumerate(returns):
            alpha = .25 + .75 * (abs(item) / max_abs_return)
            colors[i] = (1.0, .33, .33, alpha) if item < 0 else (
                .33, 1.0, .33, alpha)

        # Create the plot and format y ticks as percents.
        returns_bar_plot = returns.plot(kind='bar', color=colors)
        y_ticks = returns_bar_plot.get_yticks()
        returns_bar_plot.set_yticklabels([
            '{:3.1f}%'.format(tick * 100) for tick in y_ticks])

        return returns_bar_plot

    def get_report(self):
        """Creates the entire report.
        """
        subject = self._config['subject_format'] % str(
            self._daily['adj_close'].index[-1].date())
        body = ''

        plt.style.use('ggplot')
        plt.figure()
        self.get_returns_bar_plot(1)
        plt.show()

        return {'subject': subject, 'body': body}
