# MarketReport
MarketReport scrapes daily historical data about exchange-traded financial instruments (e.g. closing prices) from the web. It validates this data, saves it to disk, and uses it to generate email reports analyzing performance.

* Examples
  * [Portfolio report](https://github.com/peterbrandt84/market_report/blob/master/portfolio_report_example.png)
  * [Universe report](https://github.com/peterbrandt84/market_report/blob/master/universe_report_example.txt)

## Dependencies
Note: other environments will very likely work with no or minimal changes. But, this is what was used to develop MarketReport.
* OS X 10.11.2
* Python 2.7.10
* Third party
  * numpy 1.10.4
  * pandas 0.17.1
  * Pillow 3.1.1
  * PyYAML 3.11
  * [tor\_scraper](https://github.com/peterbrandt84/tor_scraper)

## Usage
See [main.py](https://github.com/peterbrandt84/market_report/blob/master/main.py) for example usage.

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature.'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## License
[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

## Contact
peterbrandt84@gmail.com