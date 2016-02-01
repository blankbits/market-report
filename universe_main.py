#!/usr/bin/python

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

"""TODO

TODO: Usage!
"""

import argparse
import logging
import logging.config
import sys

import yaml

import emailer
import historical_data
import universe_report

def main():
    """Begin executing main logic of the script.
    """
    # Parse command line args.
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', metavar='FILE', help='config YAML',
                        default='config.yaml')
    parser.add_argument('--symbols_file', metavar='FILE', help=(
        'historical_data_config symbols_file'))
    parser.add_argument('--output_dir', metavar='FILE', help=(
        'historical_data_config output_dir'))
    parser.add_argument('--start_date', metavar='YYYYMMDD', help=(
        'historical_data_config start_date'))
    parser.add_argument('--end_date', metavar='YYYYMMDD', help=(
        'historical_data_config end_date'))
    args = parser.parse_args()

    # Load config and overwrite any values set by optional command line args.
    with open(args.config_file, 'r') as config_file:
        config = yaml.load(config_file.read())
    if args.symbols_file is not None:
        config['historical_data_config']['symbols_file'] = args.symbols_file
    if args.output_dir is not None:
        config['historical_data_config']['output_dir'] = args.output_dir
    if args.start_date is not None:
        config['historical_data_config']['start_date'] = args.start_date
    if args.end_date is not None:
        config['historical_data_config']['end_date'] = args.end_date
    
    # Setup logger.
    logging.config.dictConfig(config['logging_config'])
    logger = logging.getLogger(__name__)

    # Get daily historical data.
    data = historical_data.HistoricalData(config['historical_data_config'],
                                          config['tor_scraper_config'])
    daily = data.get_daily()
    if daily is None:
        logger.error('No daily dataframe')
        return

    # Create and send email for universe report.
    universe = universe_report.UniverseReport(daily).get_default_report()
    sender = emailer.Emailer(config['emailer_config'])
    sender.send('Russell 3000 Report -- ' + (
        config['historical_data_config']['end_date']), universe)

# If in top-level script environment, run main().
if __name__ == '__main__':
    main()
