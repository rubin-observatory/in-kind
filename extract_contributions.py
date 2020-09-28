# ======================================================================

import inkind

# ======================================================================
# Run with python extract_contributions.py > BUL-NAO.csv

gdoc = {}
# Proposal Template:
gdoc["BUL-NAO"] = "https://docs.google.com/document/d/1NDnIvLaiJ9PRXGFwVmU9aMQaqJWnNstAqNUjPUoduio/edit"


proposal = {}
for program in gdoc:
    proposal[program] = inkind.Proposal(program, gdoc[program], vb=False)
    proposal[program].download()
    proposal[program].read()
    proposal[program].print_csv()
    # proposal[program].print_SOW()
