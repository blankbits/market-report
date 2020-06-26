# MarketReport
MarketReport scrapes daily historical data about exchange-traded financial instruments (e.g. closing prices) from the web. It validates this data, saves it to disk, and uses it to generate email reports analyzing performance.

* Examples
  * [Portfolio report](portfolio_report_example.png)
  * [Universe report](universe_report_example.txt)

## Dependencies
Note: other environments will very likely work with no or minimal changes. But, this is what was used to develop MarketReport.
* Ubuntu Trusty 14.04
* Python 2.7.6
* Third party
  * Pillow 3.2.0
  * PyYAML 3.10
  * numpy 1.11.0
  * matplotlib 1.5.1
  * pandas 0.18.1
  * [tor\_scraper](https://github.com/blankbits/tor_scraper)

## Usage
See [main.py](main.py) for example usage.

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature.'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## License
[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)
