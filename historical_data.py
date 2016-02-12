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

"""HistoricalData scrapes daily historical data from Yahoo Finance.

It scrapes, performs simple validation, and saves the result to disk as CSV and
pandas dataframes. It prefers to load data from files if they already exist.
This is convenient in the event scraping is interrupted and must be restarted.

Example:
    import historical_data
    data = historical_data.HistoricalData({
        'symbols_file': 'symbols.csv',
        'output_dir': 'data/20160115/',
        'end_date': '20160115',
        'start_date': '20150701',
    }, tor_scraper_config)  # See tor_scraper documentation.
    daily_data = data.get_daily()
"""

import csv
import io
import logging
import os
import pickle

import numpy as np
import pandas as pd

import tor_scraper

class HistoricalData(object):
    """Contains the entire historical_data module.
    """
    def __init__(self, historical_data_config, tor_scraper_config):
        """HistoricalData must be initialized with a args similar to those shown
        in the example at the top of this file.

        Args:
            historical_data_config: Determines the behavior of this instance.
            tor_scraper_config: Passed through to tor_scraper.
        """
        self._config = historical_data_config
        self._tor_scraper_config = tor_scraper_config
        self._logger = logging.getLogger(__name__)

    def get_daily(self):
        """Fetch up-to-date data either from disk or from the web.
        """
        # If valid pickle for data already exists, return that. If not, create
        # output dir if needed and proceed with scrape.
        pickle_path = self._config['output_dir'] + 'daily.pickle'
        if os.path.exists(pickle_path):
            self._logger.info('Pickle file already exists for end_date: ' +
                              self._config['end_date'])
            with open(pickle_path, 'rb') as pickle_file:
                return pickle.load(pickle_file)
        if not os.path.exists(self._config['output_dir']):
            os.makedirs(self._config['output_dir'])

        # Holds raw data for scrape.
        scrape_data = {}

        # Init tor_scraper, add scrape tasks, populate data for existing files.
        scraper = tor_scraper.TorScraper(self._tor_scraper_config)
        with open(self._config['symbols_file'], 'rb') as symbols_file:
            csv_reader = csv.reader(symbols_file, delimiter=',')
            for row in csv_reader:
                symbol_name = row[1]
                output_path = self._config['output_dir'] + symbol_name + '.csv'
                if int(row[2]) == 0:
                    self._logger.info('Skipping symbol: ' + symbol_name)
                elif os.path.exists(output_path):
                    self._logger.info('File already exists: ' + output_path)
                    with open(output_path, 'rb') as output_file:
                        scrape_data[symbol_name] = output_file.read()
                else:
                    url = self.get_url(symbol_name, self._config['start_date'],
                                       self._config['end_date'])
                    scraper.add_scrape(url, {'output_path': output_path,
                                             'scrape_data': scrape_data,
                                             'symbol_name': symbol_name},
                                       self._scrape_handler)

        # Start scraping, blocks until finished.
        scraper.run()

        # Get dataframes, write pickle if applicable, and return.
        daily = self._build_dataframes(scrape_data)
        if daily is not None:
            with open(pickle_path, 'w') as output_file:
                self._logger.info('Dumping dataframes to pickle file: ' +
                                  pickle_path)
                pickle.dump(daily, output_file)
        return daily

    def _build_dataframes(self, scrape_data):
        """Validate and combine raw scrape data into dataframes.
        """
        # Create dataframes for prices and volume.
        self._logger.info('Creating dataframes')
        is_valid = True
        drop_columns = []
        daily = {}
        close = {}
        adj_close = {}
        volume = {}
        for key, value in scrape_data.iteritems():
            if value is None:
                is_valid = False
            else:
                csv_data = pd.read_csv(io.StringIO(unicode(value)))
                csv_data['Date'] = csv_data['Date'].apply(pd.to_datetime)
                csv_data = csv_data.set_index('Date')
                close[key] = csv_data['Close']
                adj_close[key] = csv_data['Adj Close']
                volume[key] = csv_data['Volume']

        daily['close'] = pd.DataFrame(close)
        daily['adj_close'] = pd.DataFrame(adj_close)
        daily['volume'] = pd.DataFrame(volume)

        # Validate dataframes.
        self._logger.info('Validating dataframes')
        end_date = pd.to_datetime(self._config['end_date'])
        if daily['adj_close'].index.max() != end_date or (
                daily['volume'].index.max() != end_date):
            self._logger.error('End date mismatch')
            is_valid = False
        if np.any(daily['adj_close'].isnull()):
            columns = daily['adj_close'].columns[
                daily['adj_close'].isnull().any(axis=0)].values
            drop_columns.extend(columns)
            self._logger.error('Price data contains nulls: ' +
                               ', '.join(columns))
            is_valid = False
        if np.any(daily['volume'].isnull()):
            columns = daily['volume'].columns[
                daily['volume'].isnull().any(axis=0)].values
            drop_columns.extend(columns)
            self._logger.error('Volume data contains nulls: ' +
                               ', '.join(columns))
            is_valid = False
        if np.any(daily['volume'] == 0):
            columns = daily['volume'].columns[
                (daily['volume'] == 0).any(axis=0)].values
            drop_columns.extend(columns)
            self._logger.error('Volume data contains zeros: ' +
                               ', '.join(columns))
            is_valid = False

        # If validation fails, log error and drop any responsible columns.
        if is_valid is False:
            self._logger.error('Dataframes validation failed')
            if len(drop_columns) > 0:
                self._logger.warning('Dropping columns: ' +
                                     ', '.join(drop_columns))
                daily['adj_close'].drop(drop_columns, axis=1, inplace=True)
                daily['volume'].drop(drop_columns, axis=1, inplace=True)

        # Sort rows by datetime in ascending order.
        daily['adj_close'].sort_index(inplace=True)
        daily['volume'].sort_index(inplace=True)

        return daily

    def _scrape_handler(self, url, context, result):
        """Stores the result of scrapes in memory and writes to file.
        """
        # Validate raw scrape data.
        if not str(result).startswith(
                'Date,Open,High,Low,Close,Volume,Adj Close'):
            self._logger.error('Error scraping url: ' + url)
            context['scrape_data'][context['symbol_name']] = None
            return

        output_path = context['output_path']
        self._logger.info('Writing file: ' + output_path + ' for url: ' + url)
        with open(output_path, 'w') as output_file:
            output_file.write(result)

        context['scrape_data'][context['symbol_name']] = result

    @staticmethod
    def get_url(symbol_name, start_date, end_date=None):
        """Builds the url to request data for the given symbol and time period.
        Uses dates of format YYYYMMDD.

        Args:
            symbol_name: The ticker symbol for this instrument.
            start_date: First date for which to request data.
            end_date: Last date for which to request data.
        """
        start_date = start_date
        url = 'http://real-chart.finance.yahoo.com/table.csv?ignore=.csv'
        url += '&s=' + symbol_name
        url += '&a=%s&b=%s&c=%s' % (int(start_date[4:6]) - 1, start_date[6:],
                                    start_date[0:4])
        if end_date != None:
            end_date = end_date
            url += '&d=%s&e=%s&f=%s' % (int(end_date[4:6]) - 1, end_date[6:],
                                        end_date[0:4])
        return url
