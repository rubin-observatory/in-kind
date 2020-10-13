# in-kind

_Phil Marshall_
_Rubin Observatory In-kind Program Coordination Team_

Python package for parsing in-kind proposals, scraping out the proposed contributions, and automatically generating SOWs and detailed plans. Designed for use by the Rubin IPC team, but made available to all participants in the Rubin in-kind program to help check their proposal work.

## Examples

1. Scrape proposed contributions out of the submitted proposal Google documents, and producing a CSV format data file for ingestion into the Rubin/CEC review spreadsheet.

```bash
./extract_contributions.py proposals.csv > contributions.csv
```

2. Parse a proposal Google document and produce two plain text files, 1) a Statement of Work and 2) a Detailed Plan.

## Installation

Pip install directly from GitHub as follows, in a suitable folder:
```bash
pip install -e git+git://github.com/rubin-observatory/in-kind.git@master#egg=inkind
```
The `-e` _should_ allow you to easily go in and edit the code in a branch, and then commit and push changes to your GitHub fork/branch. More instructions to follow...

## License

This code is distributed under the MIT license, and is being developed sporadically by the Rubin operations team. If you'd like to help out, please [send us an issue!](https://github.com/rubin-observatory/in-kind/issues/new?body=@drphilmarshall)
