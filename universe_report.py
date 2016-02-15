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

"""UniverseReport generates text-based visualizations of past performance of a
universe of financial instruments e.g. components of a market index.

Example:
    # See historical_data documentation for more info.
    data = historical_data.HistoricalData(historical_data_config,
                                          tor_scraper_config)
    daily = data.get_daily()
    if daily is None:
        return
    print universe_report.UniverseReport({
        'subject_format': 'Universe Report -- %s',
        'body_returns': {
            1: {'bins_start': -.2, 'bins_stop': .22, 'bins_step': .02, },
            20: {'bins_start': -.5, 'bins_stop': .55, 'bins_step': .05, },
        },
        'body_stats': {
            1: {'count': 10, },
        },
    }, daily).get_report()
"""

import sys

import numpy as np

import text_utils

class UniverseReport(object):
    """Contains all functionality for the universe_report module.
    """
    def __init__(self, universe_report_config, daily):
        """UniverseReport must be initialized with args similar to those shown
        in the example at the top of this file.

        Args:
            universe_report_config: Determines the behavior of this instance.
            daily: pandas.DataFrame of prices of the same type returned by
                historical_data.get_daily(). Rows represent dates in ascending
                order, and columns represent financial instruments.
        """
        self._config = universe_report_config
        self._daily = daily

    def get_returns_section(self, offset, bins=None):
        """Creates a multi-line string containing a column of top winners and
        losers on the left, and a histogram of all returns on the right.

        Args:
            offset: Number of rows (days) back to go when calculating returns.
            bins: List of boundaries between histogram bins in ascending order.
        """
        # returns = ((self._daily['adj_close'].iloc[0, :] - (
        #     self._daily['adj_close'].iloc[offset, :])) / (
        #         self._daily['adj_close'].iloc[offset, :])).sort_values()
        returns = ((self._daily['adj_close'].iloc[-1, :] - (
            self._daily['adj_close'].iloc[-(offset + 1), :])) / (
                self._daily['adj_close'].iloc[-(offset + 1), :])).sort_values()

        # If no bins provided, create default of 20 equally spaced bins.
        if bins is None:
            bins = np.arange(returns.min() - sys.float_info.epsilon,
                             returns.max() + sys.float_info.epsilon,
                             .05 * (returns.max() - returns.min()))
        else:
            # Possibly add bins at either end to ensure all values are counted.
            if returns.min() < bins.min():
                bins = np.insert(bins, 0, returns.min() - (
                    sys.float_info.epsilon))
            if returns.max() > bins.max():
                bins = np.append(bins, returns.max() + sys.float_info.epsilon)

        returns_hist = text_utils.get_histogram(returns, bins, 0, True)

        # If there is space for winners and losers and at least one empty line
        # separating them, then include them.
        extreme_count = int(np.floor((bins.size - 1) * .5)) - 1
        if extreme_count > 0:
            returns_col = text_utils.get_column(returns[:extreme_count], 1, (
                True))
            returns_col += ''.join('\n' * (bins.size - 2 * extreme_count - (
                1)))
            returns_col += text_utils.get_column(returns[-extreme_count:], 1, (
                True))
        else:
            returns_col = ''

        return text_utils.join_lines([returns_col, returns_hist], '    ')

    def get_stats_section(self, offset, count):
        """Creates a multi-line string with several columns of stats about the
        universe for a given time period.

        Args:
            offset: Number of rows (days) back to go when calculating stats.
                This must be at least 4 so that there are 2 periods to compare.
            count: Number of values to include for volatility and volume.
        """
        period_end = self._daily['adj_close'].shape[0]
        period_start = period_end - offset
        period_midpoint = period_end - int(np.around(offset * .5))

        # Prices with the most recent value at a max or min for the period.
        price_at_high_cols = self._daily['adj_close'].iloc[
            period_start:, :].max(axis=0) == self._daily['adj_close'].iloc[
                -1, :]
        price_at_high = 'At High\n' + text_utils.get_column(
            self._daily['adj_close'].ix[-1, price_at_high_cols], 2)
        price_at_low_cols = self._daily['adj_close'].iloc[
            period_start:, :].min(axis=0) == self._daily['adj_close'].iloc[
                -1, :]
        price_at_low = 'At Low\n' + text_utils.get_column(
            self._daily['adj_close'].ix[-1, price_at_low_cols], 2)

        # Change in price stdev from the first to second half of the period.
        # Ranges are inclusive because we care about differences across days.
        first_range = range(period_start, period_midpoint)
        second_range = range(period_midpoint - 1, period_end)
        volatility_change = self._daily['adj_close'].iloc[first_range, :].std(
            axis=0) / (self._daily['adj_close'].iloc[second_range, :].std(
                axis=0))
        volatility_change = 'Volatility Chg\n' + text_utils.get_column(
            volatility_change.sort_values(ascending=False)[range(count)], 2, (
                True))

        # Change in volume from the first to second half of the period.
        # Ranges are not inclusive since we are summing volume for each day.
        first_range = range(period_start, period_midpoint)
        second_range = range(period_midpoint, period_end)
        volume_change = self._daily['volume'].iloc[first_range, :].sum(
            axis=0) / (self._daily['volume'].iloc[second_range, :].sum(axis=0))
        volume_change = 'Volume Chg\n' + text_utils.get_column(
            volume_change.sort_values(ascending=False)[range(count)], 2, True)

        return text_utils.join_lines([price_at_high, price_at_low, (
            volatility_change), volume_change], '    ')

    def get_report(self):
        """Creates the entire report including returns and stats sections
        determined by the config.
        """
        subject = self._config['subject_format'] % str(
            self._daily['adj_close'].index[-1].date())
        body = ''
        for key, value in self._config['body_returns'].iteritems():
            body += '%s Day Returns\n-------------\n' % str(key)
            body += self.get_returns_section(key, np.arange(
                float(value['bins_start']), float(value['bins_stop']),
                float(value['bins_step'])))
        for key, value in self._config['body_stats'].iteritems():
            body += '%s Day Stats\n------------\n' % str(key)
            body += self.get_stats_section(key, value['count'])
        return {'subject': subject, 'body': body}
