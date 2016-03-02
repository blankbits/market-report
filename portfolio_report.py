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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL

import plot_utils

class PortfolioReport(object):
    """Contains all functionality for the portfolio_report module.
    """
    _STYLE_SHEET = 'ggplot'
    _TEXT_COLOR = (.3, .3, .3, 1.0)
    _BAR_ALPHA = .67
    _TITLE_DOLLAR_FORMAT = '${:,.2f}'
    _REPORT_COLS = 2

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

    def _get_percent_returns(self, cumulative=False):
        """Calculate percent returns for the entire time period, either
        cumulative from the beginning or separately for each day.
        """
        if cumulative is True:
            return self._daily['adj_close'] / (
                self._daily['adj_close'].ix[0, :]) - 1.0
        else:
            return self._daily['adj_close'].pct_change()

    def _get_dollar_values(self, group=False):
        """Calculate the value of portfolio holdings using closing prices.
        Optionally aggregate the values into groups provided in config.
        """
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

        if group is True:
            dollar_values = self._sum_symbol_groups(dollar_values)
        return dollar_values

    def _get_dollar_returns(self, group=False):
        """Calculate the dollar returns for portfolio holdings. Optionally
        aggregate the returns into groups provided in config.
        """
        dollar_values = self._get_dollar_values()
        percent_returns = self._get_percent_returns()
        dollar_returns = dollar_values * percent_returns
        if group is True:
            dollar_returns = self._sum_symbol_groups(dollar_returns)
        return dollar_returns

    def _get_profit_and_loss(self):
        """Calculate the profit and loss of the portfolio over time.
        """
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

    def _sum_symbol_groups(self, data_frame):
        """Sum columns of dataframe using symbol_groups in config.
        """
        sum_data_frame = pd.DataFrame()
        for key, value in sorted(self._config['symbol_groups'].iteritems()):
            sum_data_frame[key] = data_frame[value].sum(1)
        return sum_data_frame

    def plot_dollar_change_bars(self, group=False):
        """Plot the change in dollars for the most recent day as a bar plot.

        Args:
            group: Whether to aggregate based on symbol_groups in config.
        """
        dollar_values = self._get_dollar_values(group).ix[-1, :]
        dollar_returns = self._get_dollar_returns(group).ix[-1, :]
        percent_returns = dollar_returns / dollar_values
        labels = plot_utils.get_percent_strings(percent_returns)
        bar_colors = plot_utils.get_conditional_colors(
            percent_returns, self._BAR_ALPHA)
        title = ('1-Day Change | ' + self._TITLE_DOLLAR_FORMAT + (
            '\n')).format(np.sum(dollar_returns))

        plot = dollar_returns.plot(kind='bar', color=bar_colors)
        plot.set_title(title, color=self._TEXT_COLOR)
        plot.set_xticklabels(dollar_returns.index, rotation=0)
        plot_utils.format_y_ticks_as_dollars(plot)
        plot_utils.add_bar_labels(plot, labels, self._TEXT_COLOR)
        return plot

    def plot_percent_return_lines(self):
        """Plot percent returns for each symbol for the entire time period as a
        line plot.
        """
        percent_returns = self._get_percent_returns(True)
        title = 'Symbol Returns\n'

        plot = percent_returns.plot(kind='line', ax=plt.gca())
        plot.set_title(title, color=self._TEXT_COLOR)
        plot_utils.format_x_ticks_as_dates(plot)
        plot_utils.format_y_ticks_as_percents(plot)
        plot_utils.format_legend(plot, self._TEXT_COLOR)
        return plot

    def plot_dollar_value_bars(self, group=False):
        """Plot the dollar value of portfolio holdings for the most recent day
        as a bar plot.

        Args:
            group: Whether to aggregate based on symbol_groups in config.
        """
        dollar_values = self._get_dollar_values(group).ix[-1, :]
        percents = dollar_values / np.sum(dollar_values)
        labels = plot_utils.get_percent_strings(percents)
        title = 'Portfolio Weights\n'

        plot = dollar_values.plot(kind='bar', alpha=self._BAR_ALPHA)
        plot.set_title(title, color=self._TEXT_COLOR)
        plot.set_xticklabels(dollar_values.index, rotation=0)
        plot_utils.format_y_ticks_as_dollars(plot)
        plot_utils.add_bar_labels(plot, labels, self._TEXT_COLOR)
        return plot

    def plot_dollar_value_lines(self, group=False):
        """Plot the dollar value of portfolio holdings for the entire time
        period as a line plot.

        Args:
            group: Whether to aggregate based on symbol_groups in config.
        """
        dollar_values = self._get_dollar_values(group)
        dollar_values['TOTAL'] = dollar_values.sum(1)
        title = ('Portfolio Value | ' + self._TITLE_DOLLAR_FORMAT + (
            '\n')).format(dollar_values['TOTAL'].ix[-1])

        plot = dollar_values.plot(kind='line', ax=plt.gca())
        plot.set_title(title, color=self._TEXT_COLOR)
        plot_utils.format_x_ticks_as_dates(plot)
        plot_utils.format_y_ticks_as_dollars(plot)
        plot_utils.format_legend(plot, self._TEXT_COLOR)
        return plot

    def plot_profit_and_loss_lines(self):
        """Plot the profit and loss of the portfolio for the entire time period
        as a line plot.

        Args:
            group: Whether to aggregate based on symbol_groups in config.
        """
        profit_and_loss = self._get_profit_and_loss()
        title = ('Cumulative P&L | ' + self._TITLE_DOLLAR_FORMAT + (
            '\n')).format(profit_and_loss[-1])

        plot = profit_and_loss.plot(kind='line', ax=plt.gca())
        plot.set_title(title, color=self._TEXT_COLOR)
        plot_utils.format_x_ticks_as_dates(plot)
        plot_utils.format_y_ticks_as_dollars(plot)
        return plot


    def get_report(self):
        """Creates the entire report composed of individual plots.
        """
        subject = self._config['subject_format'] % str(
            self._daily['adj_close'].index[-1].date())
        body = ''

        plt.style.use(self._STYLE_SHEET)

        # Create list of plot images to include in the report image.
        plot_images = []
        plot_images.append(plot_utils.get_plot_image(
            self.plot_dollar_change_bars, group=True))
        plot_images.append(plot_utils.get_plot_image(
            self.plot_dollar_change_bars))
        plot_images.append(plot_utils.get_plot_image(
            self.plot_dollar_value_bars, group=True))
        plot_images.append(plot_utils.get_plot_image(
            self.plot_dollar_value_bars))
        plot_images.append(plot_utils.get_plot_image(
            self.plot_dollar_value_lines, group=True))
        plot_images.append(plot_utils.get_plot_image(
            self.plot_dollar_value_lines))
        plot_images.append(plot_utils.get_plot_image(
            self.plot_profit_and_loss_lines))
        plot_images.append(plot_utils.get_plot_image(
            self.plot_percent_return_lines))
        plot_images = [PIL.Image.open(x) for x in plot_images]

        # Arrange plot images in a grid in the report image.
        plot_width = plot_images[0].size[0]
        plot_height = plot_images[0].size[1]
        report_image = PIL.Image.new('RGB', (
            plot_width * self._REPORT_COLS, plot_height * int(
                np.ceil(len(plot_images) / self._REPORT_COLS))), 'white')
        for i, item in enumerate(plot_images):
            report_image.paste(item, ((i % self._REPORT_COLS) * plot_width, int(
                np.floor(i / self._REPORT_COLS)) * plot_height))

        # Display report image to user.
        report_image.show()

        return {'subject': subject, 'body': body}
