# in-kind

_Phil Marshall_
_Rubin Observatory In-kind Program Coordination Team_

Python package for parsing in-kind proposals, scraping out the proposed contributions, and automatically generating SOWs. Designed for use by the Rubin IPC team, but made available publicly, e.g. to help participants in the Rubin in-kind program to check their edits to their program descriptions.

## Examples

1. Scrape proposed contributions out of the submitted proposal Google documents, and producing a CSV format data file for ingestion into either the Rubin/CEC review spreadsheet or the IPC team's contribution tracker.

```bash
./extract_contributions.py proposals.csv > contributions.csv
```

2. Parse a proposal Google document (or a set of them) and produce a plain text Statement of Work. (Under construction.)

```bash
./extract_sows.py proposals.csv > sows.txt
```

## Installation

Pip install directly from GitHub as follows, in a suitable folder:
```bash
pip install -e git+git://github.com/rubin-observatory/in-kind.git@master#egg=inkind
```
The `-e` _should_ allow you to easily go in and edit the code in a branch, and then commit and push changes to your GitHub fork/branch. More instructions to follow...

## License

This code is distributed under the MIT license, and is being developed sporadically by the Rubin operations team. If you'd like to help out, please [send us an issue!](https://github.com/rubin-observatory/in-kind/issues/new?body=@drphilmarshall)
