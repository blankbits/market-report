#!/usr/bin/python
"""Downloads daily historical data from Yahoo Finance using Tor to enable
circumventing any rate limits.
"""

import logging
import logging.config
import sys

import yaml

import historical_data
import universe_report

def usage():
    """Print Unix-style usage string.
    """
    print 'usage: test.py [config_file]'

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

    universe = universe_report.UniverseReport(daily).to_string()
    print universe

# If in top-level script environment, run main().
if __name__ == '__main__':
    main()
