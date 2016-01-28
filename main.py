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

import logging
import logging.config
import sys

import yaml

import emailer
import historical_data
import universe_report

def usage():
    """Print Unix-style usage string.
    """
    print 'usage: main.py [config_file]'

def main():
    """Begin executing main logic of the script.
    """
    # Load config and setup logger
    if len(sys.argv) == 1:
        config_path = 'config.yaml'  # Default config file.
    elif len(sys.argv) == 2:
        if sys.argv[1] in ['-h', '--help']:
            usage()
            sys.exit()

        config_path = sys.argv[1]
    else:
        usage()
        sys.exit(2)
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file.read())

    logging.config.dictConfig(config['logging_config'])
    logger = logging.getLogger(__name__)

    # config['historical_data_config']['end_date'] = '20160115'
    # config['historical_data_config']['output_dir'] = 'blarg/'
    blah = historical_data.HistoricalData(config['historical_data_config'],
                                          config['tor_scraper_config'])

    daily = blah.get_daily()
    if daily is None:
        logger.error('No daily dataframe')
        return

    universe = universe_report.UniverseReport(daily).get_default_report()
    print universe

    sender = emailer.Emailer(config['emailer_config'])
    sender.send('Russell 3000 Report -- 4444-55-22', universe)

# If in top-level script environment, run main().
if __name__ == '__main__':
    main()
