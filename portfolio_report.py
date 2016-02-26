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

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class PortfolioReport(object):
    """Contains all functionality for the portfolio_report module.
    """
    _STYLE_SHEET = 'ggplot'
    _TEXT_COLOR = (.3, .3, .3, 1.0)

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

    def _get_returns(self, offset):
        return ((self._daily['adj_close'].iloc[-1, :] - (
            self._daily['adj_close'].iloc[-(offset + 1), :])) / (
                self._daily['adj_close'].iloc[-(offset + 1), :])).sort_index()

    def _get_dollar_values(self):
        dates = sorted(self._config['dates'])
        # Copy dataframe and zero data before earliest portfolio date.
        dollar_values = self._daily['close'].copy()
        dollar_values.ix[
            dollar_values.index < pd.to_datetime(str(dates[0])), :] = 0.0

        # Loop thru dates and calculate each date range using bitmask index.
        for i, item in enumerate(dates):
            index = dollar_values.index >= pd.to_datetime(str(item))
            if i < (len(dates) - 1):
                index = index & (
                    dollar_values.index < pd.to_datetime(str(dates[i + 1])))
            for key in list(dollar_values.columns.values):
                value = self._config['dates'][item]['symbols'].get(key)
                if value is None:
                    dollar_values.ix[index, key] = 0.0
                else:
                    dollar_values.ix[index, key] *= value * self._config[
                        'value_ratio']

        return dollar_values

    def _get_profit_and_loss(self):
        profit_and_loss = self._get_dollar_values().sum(1)
        dates = sorted(self._config['dates'])

        # Correct spike on first portfolio date.
        first_date = np.argmax(
            profit_and_loss.index >= pd.to_datetime(str(dates[0])))
        profit_and_loss.ix[first_date:] -= profit_and_loss.ix[first_date]

        # Adjust for capital changes.
        for i, item in enumerate(dates):
            if i > 0:
                index = profit_and_loss.index >= pd.to_datetime(str(item))
                profit_and_loss.ix[index] -= self._config[
                    'dates'][item]['capital_change'] * self._config[
                        'value_ratio']

        return profit_and_loss

    @staticmethod
    def _get_return_colors(returns):
        # Color winners green, losers red, and adjust color by magnitude.
        max_abs_return = max(np.abs(returns))
        colors = [(0.0, 0.0, 0.0, 0.0)] * len(returns)
        for i, item in enumerate(returns):
            intensity = .75 * (1.0 - (abs(item) / max_abs_return))
            colors[i] = (1.0, intensity, intensity, .67) if item < 0 else (
                intensity, 1.0, intensity, .67)
        return colors

    @staticmethod
    def _format_x_ticks_as_dates(plot):
        plot.xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y-%m-%d'))
        plot.set_xlabel('')
        return plot

    @staticmethod
    def _format_y_ticks_as_percents(plot):
        y_ticks = plot.get_yticks()
        plot.set_yticklabels([
            '{:3.1f}%'.format(tick * 100.0) for tick in y_ticks])
        return plot

    @staticmethod
    def _format_y_ticks_as_dollars(plot):
        y_ticks = plot.get_yticks()
        plot.set_yticklabels(['${:,.0f}'.format(tick) for tick in y_ticks])
        return plot

    @staticmethod
    def _format_legend(plot, text_color):
        # Draw legend outside plot and shrink axes area to fit.
        legend = plot.legend(loc='center right', fontsize=10.0, bbox_to_anchor=(
            1.2, .5), frameon=False)
        for text in legend.get_texts():
            text.set_color(text_color)

        box = plt.gca().get_position()
        plt.gca().set_position([box.x0, box.y0,
                                box.width * .9, box.height])
        return plot

    @staticmethod
    def _add_bar_labels(plot, labels, text_color):
        rects = plot.patches
        for rect, label in zip(rects, labels):
            height = rect.get_height() * (-1.0 if rect.get_y() < 0 else 1.0)
            vert_align = 'top' if rect.get_y() < 0 else 'bottom'
            plot.text(rect.get_x() + rect.get_width() * .5, height, (
                label), ha='center', va=vert_align, color=text_color)
        return plot

    def plot_dollar_change_bars(self):
        percent_returns = self._get_returns(1)
        colors = self._get_return_colors(percent_returns)

        # Use most recent portfolio from config to convert to dollar returns.
        dollar_returns = percent_returns * self._config['value_ratio']
        portfolio = self._config['dates'][max(self._config['dates'], key=int)]
        for i in dollar_returns.index:
            dollar_returns[str(i)] *= self._daily['adj_close'].ix[
                -2, str(i)] * (portfolio['symbols'][str(i)])

        plot = dollar_returns.plot(kind='bar', color=colors)
        plot.set_title('1 Day Change | ${:,.2f}\n'.format(
            np.sum(dollar_returns)), color=self._TEXT_COLOR)
        self._format_y_ticks_as_dollars(plot)
        labels = ['{:3.1f}%'.format(x * 100.0) for x in percent_returns]
        self._add_bar_labels(plot, labels, self._TEXT_COLOR)
        return plot

    def plot_percent_return_lines(self):
        returns = self._daily['adj_close'] / (
            self._daily['adj_close'].ix[0, :]) - 1.0

        plot = returns.plot(kind='line', ax=plt.gca())
        plot.set_title('Change %\n', color=self._TEXT_COLOR)
        self._format_x_ticks_as_dates(plot)
        self._format_y_ticks_as_percents(plot)
        self._format_legend(plot, self._TEXT_COLOR)

        return plot

    def plot_dollar_value_bars(self):
        dollar_values = self._get_dollar_values().ix[-1, :]
        percents = dollar_values / np.sum(dollar_values)

        plot = dollar_values.plot(kind='bar', alpha=.67)
        plot.set_title('\$ Value | ${:,.2f}\n'.format(
            np.sum(dollar_values)), color=self._TEXT_COLOR)
        self._format_y_ticks_as_dollars(plot)
        labels = ['{:3.1f}%'.format(x * 100.0) for x in percents]
        self._add_bar_labels(plot, labels, self._TEXT_COLOR)
        return plot

    def plot_dollar_value_lines(self):
        dollar_values = self._get_dollar_values()
        dollar_values['TOTAL'] = dollar_values.sum(1)

        plot = dollar_values.plot(kind='line', ax=plt.gca())
        plot.set_title('\$ Value\n', color=self._TEXT_COLOR)
        self._format_x_ticks_as_dates(plot)
        self._format_y_ticks_as_dollars(plot)
        self._format_legend(plot, self._TEXT_COLOR)
        return plot

    def plot_profit_and_loss_lines(self):
        profit_and_loss = self._get_profit_and_loss()

        plot = profit_and_loss.plot(kind='line', ax=plt.gca())
        plot.set_title('Cumulative P&L | ${:,.2f}\n'.format(
            profit_and_loss[-1]), color=self._TEXT_COLOR)
        self._format_x_ticks_as_dates(plot)
        self._format_y_ticks_as_dollars(plot)
        #self._format_legend(plot, self._TEXT_COLOR)
        return plot

    def get_report(self):
        """Creates the entire report.
        """
        subject = self._config['subject_format'] % str(
            self._daily['adj_close'].index[-1].date())
        body = ''

        plt.style.use(self._STYLE_SHEET)
        plt.figure()
        self.plot_dollar_change_bars()
        plt.figure()
        self.plot_percent_return_lines()
        plt.figure()
        self.plot_dollar_value_bars()
        plt.figure()
        self.plot_dollar_value_lines()
        plt.figure()
        self.plot_profit_and_loss_lines()
        plt.show()

        return {'subject': subject, 'body': body}
