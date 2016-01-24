import sys

import numpy as np

import text_utils

class UniverseReport(object):
    def __init__(self, daily):
        self._daily = daily

    def get_returns_report(self, offset, bins=None):
        returns = ((self._daily['price'].iloc[0, :] - (
            self._daily['price'].iloc[offset, :])) / (
                self._daily['price'].iloc[offset, :]).sort_values())

        if bins is None:
            bins = np.arange(returns.min() - sys.float_info.epsilon,
                             returns.max() + sys.float_info.epsilon,
                             .05 * (returns.max() - returns.min()))
        else:
            if returns.min() < bins.min():
                bins = np.insert(bins, 0, returns.min() - (
                    sys.float_info.epsilon))
            if returns.max() > bins.max():
                bins = np.append(bins, returns.max() + sys.float_info.epsilon)

        returns_hist = text_utils.get_histogram(100 * returns, 100 * bins, 0, (
            True))
        extreme_count = int(np.floor((bins.size - 1) * .5)) - 1
        if extreme_count > 0:
            returns_col = text_utils.get_column(100 * returns[:extreme_count], (
                1), True)
            returns_col += ''.join('\n' * (bins.size - 2 * extreme_count - (
                1)))
            returns_col += text_utils.get_column(100 * (
                returns[-extreme_count:]), 1, True)
        else:
            returns_col = ''

        return text_utils.join_lines([returns_col, returns_hist], '    ')

    def get_stats_report(self, offset, count):
        price_at_high = 'At High\n' + text_utils.get_column(
            self._daily['price'].ix[0, self._daily['price'].max(axis=0) == (
                self._daily['price'].iloc[0, :])], 2)
        price_at_low = 'At Low\n' + text_utils.get_column(
            self._daily['price'].ix[0, self._daily['price'].min(axis=0) == (
                self._daily['price'].iloc[0, :])], 2)
        volatility_change = self._daily['price'].iloc[range(
            offset / 2 + 1), :].std(axis=0) / (self._daily['price'].iloc[range(
                (offset / 2), offset + 1), :].std(axis=0))
        volatility_change = 'Volatility Chg\n' + text_utils.get_column(
            100 * volatility_change.sort_values(ascending=False)[range(
                count)], 2, True)
        volume_change = self._daily['volume'].iloc[range(
            offset / 2 + 1), :].sum(axis=0) / (self._daily['volume'].iloc[range(
                (offset / 2), offset + 1), :].sum(axis=0))
        volume_change = 'Volume Chg\n' + text_utils.get_column(
            100 * volume_change.sort_values(
                ascending=False)[range(count)], 2, True)
        return text_utils.join_lines([price_at_high, price_at_low, (
            volatility_change), volume_change], '    ')

    def get_default_report(self):
        result = '1 Day Returns\n-------------\n'
        result += self.get_returns_report(1, np.arange(-.2, .22, .02))
        result += '20 Day Returns\n--------------\n'
        result += self.get_returns_report(20, np.arange(-.5, .55, .05))
        result += '20 Day Stats\n------------\n'
        result += self.get_stats_report(20, 10)
        return result
