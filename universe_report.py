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
    hd = historical_data.HistoricalData(historical_data_config,
                                        tor_scraper_config)
    daily = hd.get_daily()
    if daily is None:
        return
    print universe_report.UniverseReport(daily).get_default_report()
"""

import sys

import numpy as np

import text_utils

class UniverseReport(object):
    """Contains all functionality for the universe_report module.
    """
    def __init__(self, daily):
        """UniverseReport must be initialized with a pandas.DataFrame of prices
        of the same type returned by historical_data.get_daily(). Rows represent
        dates in ascending order, and columns represent financial instruments.

        Args:
            daily: pandas.DataFrame containing historical price data.
        """
        self._daily = daily

    def get_returns_report(self, offset, bins=None):
        """Creates a multi-line string containing a column of top winners and
        losers on the left, and a histogram of all returns on the right.

        Args:
            offset: Number of rows (days) back to go when calculating returns.
            bins: List of boundaries between histogram bins in ascending order.
        """
        # returns = ((self._daily['price'].iloc[0, :] - (
        #     self._daily['price'].iloc[offset, :])) / (
        #         self._daily['price'].iloc[offset, :])).sort_values()
        returns = ((self._daily['price'].iloc[-1, :] - (
            self._daily['price'].iloc[-(offset + 1), :])) / (
                self._daily['price'].iloc[-(offset + 1), :])).sort_values()

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

    def get_stats_report(self, offset, count):
        """Creates a multi-line string with several columns of stats about the
        universe for a given time period.

        Args:
            offset: Number of rows (days) back to go when calculating stats.
                This must be at least 4 so that there are 2 periods to compare.
            count: Number of values to include for volatility and volume.
        """
        period_end = self._daily['price'].shape[0]
        period_start = period_end - offset
        period_midpoint = period_end - int(np.around(offset * .5))

        # Prices with the most recent value at a max or min for the period.
        price_at_high_cols = self._daily['price'].iloc[
            period_start:, :].max(axis=0) == self._daily['price'].iloc[-1, :]
        price_at_high = 'At High\n' + text_utils.get_column(
            self._daily['price'].ix[-1, price_at_high_cols], 2)
        price_at_low_cols = self._daily['price'].iloc[
            period_start:, :].min(axis=0) == self._daily['price'].iloc[-1, :]
        price_at_low = 'At Low\n' + text_utils.get_column(
            self._daily['price'].ix[-1, price_at_low_cols], 2)

        # Change in price stdev from the first to second half of the period.
        # Ranges are inclusive because we care about differences across days.
        first_range = range(period_start - 1, period_midpoint)
        second_range = range(period_midpoint - 1, period_end)
        volatility_change = self._daily['price'].iloc[first_range, :].std(
            axis=0) / (self._daily['price'].iloc[second_range, :].std(axis=0))
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

    def get_default_report(self):
        """Creates a report including 1 and 20 day returns and 20 day stats. The
        offsets and bin boundaries are hard-coded.
        """
        result = '1 Day Returns\n-------------\n'
        result += self.get_returns_report(1, np.arange(-.2, .22, .02))
        result += '20 Day Returns\n--------------\n'
        result += self.get_returns_report(20, np.arange(-.5, .55, .05))
        result += '20 Day Stats\n------------\n'
        result += self.get_stats_report(20, 10)
        return result
