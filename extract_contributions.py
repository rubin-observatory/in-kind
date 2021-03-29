#!/usr/bin/env python
# ======================================================================
import sys
import getopt
import csv
import inkind
# ======================================================================

def extract_contributions(argv):
    """
    Read in a csv file containing program codes and proposal Google doc URLs and extract the proposed contributions' basic information.

    USAGE
        extract_contributions.py proposals.csv > contributions.csv

    FLAGS
        -h                  Print this message
        -v                  Verbose operation
        -f --fast           Fast operation - skip the download of the doc html
        -j --just  PRO-COD  Fast operation - only re-download the named proposal

    INPUTS
        proposal.csv    CSV file containing program codes, proposal URLs

    OUTPUTS
        stdout     Output data in CSV format

    HISTORY
        2020-09-28    started Marshall (SLAC)
    """
# ----------------------------------------------------------------------
# Handle options and arguments:
    try:
        options, inputs = getopt.getopt(argv, "hvfj:", ["help","verbose","fast","just="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        print(extract_contributions.__doc__)
        return

    vb = False
    fast = False
    updated_proposal = None
    for o, a in options:
        if o in ("-h", "--help"):
            print(extract_contributions.__doc__)
            return
        elif o in ("-v", "--verbose"):
            vb = True
        elif o in ("-f", "--fast"):
            fast = True
        elif o in ("-j", "--just"):
            fast = True
            updated_proposal = a
        else:
            assert False, "Unhandled option"

    if len(inputs) == 1:
        csvfile = inputs[0]
    else:
        print(extract_contributions.__doc__)
        return

# ----------------------------------------------------------------------
# Read 2-column CSV file in as a dictionary:

    with open(csvfile, mode='r') as infile:
        reader = csv.reader(infile)
        # Skip the header row:
        next(reader)
        gdoc = {rows[0]:rows[1] for rows in reader}


    # with open('coors_new.csv', mode='w') as outfile:
    #     writer = csv.writer(outfile)

    # Add in the Proposal Template:
    # gdoc["BUL-NAO"] = "https://docs.google.com/document/d/1NDnIvLaiJ9PRXGFwVmU9aMQaqJWnNstAqNUjPUoduio/edit"

    # Loop over proposals, reading them and generating CSV stdout.
    proposal = {}
    for program in gdoc:
        proposal[program] = inkind.Proposal(program, gdoc[program], vb=vb)
        if fast and program != updated_proposal:
            pass
        else:
            proposal[program].download()
        proposal[program].read()
        proposal[program].print_csv()
        # user_input = sys.stdin.readline().rstrip()

    return

# ======================================================================

if __name__ == '__main__':
    extract_contributions(sys.argv[1:])

# ======================================================================
