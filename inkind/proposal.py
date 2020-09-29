import requests
from html.parser import HTMLParser
import inkind

class Proposal(HTMLParser):

    def __init__(self, program, url, vb=False):
        super().__init__()
        self.gdoc = url
        self.vb = vb
        self.PROGRAM_CODE = program
        self.htmlfile = "."+program+".html"
        self.preamble = True
        self.count = 0
        self.current = None
        self.contribution = {}
        self.directory = None
        return

    def download(self):
        html = self.gdoc.replace("edit", "export?format=html")
        if self.vb: print("Downloading Gdoc as HTML via ",html)
        r = requests.get(html, allow_redirects=True)
        open(self.htmlfile, 'wb').write(r.content)
        if self.vb: print("New HTML file: ", self.htmlfile)
        return

    def read(self):
        if self.vb: print("Reading proposal from ",self.htmlfile)
        f = open(self.htmlfile, 'r')
        self.feed(f.read())
        f.close()
        return

    def print_csv(self):
        if self.vb: print("Extracted ",self.count," contributions:")
        for S in self.contribution:
            # Look up the Contribution Lead email address:
            E = self.contribution[S].match_email(self.directory)
            # Look up the contribution category:
            C = self.contribution[S].estimate_category()
            # Extract the contribution value:
            N = self.contribution[S].extract_PI_value()
            # Write out a CSV table row:
            print(self.PROGRAM_CODE+"-"+self.contribution[S].ID+","+
                  ",,"+
                  '"'+str(self.contribution[S].TITLE)+'"'+","+
                  str(self.contribution[S].URL)+","+
                  str(self.contribution[S].LEAD)+","+
                  str(self.contribution[S].EMAIL)+","+
                  str(self.contribution[S].LOI_CODE)+","+
                  str(self.contribution[S].CATEGORY)+","+
                  str(self.contribution[S].RECIPIENTS)+","+
                  '"'+self.contribution[S].one_line_SOW()+'"'+","+
                  str(self.contribution[S].VALUE)+","+
                  str(self.contribution[S].EXCEPTION))
        return

    def print_SOW(self):
        if self.vb: print("Statement of Work:")
        for S in self.contribution:
            print(self.contribution[S].print_SOW())
        return

    def handle_starttag(self, tag, attrs):
        # Detect the end of the preamble:
        if tag == "hr" and self.preamble:
            if self.vb: print("Leaving the preamble")
            self.preamble = False

        # First two headiings are the proposal title and abstract, in the document preamble - ignore these.
        if self.preamble:
            pass
        elif tag == "h2":
            if self.vb: print("Encountered a new contribution: ")
            self.count = self.count + 1
            new = inkind.Contribution()
            new.ID = "S"+str(self.count)
            self.current = new.ID
            if self.vb: print("    Contribution ID: ", new.ID)
            for attr in attrs:
                # print("     attr:", attr)
                if attr[0] == "id": heading = attr[1]
            new.URL = self.gdoc + "#heading=" + heading
            if self.vb: print("    Contribution section URL: ", new.URL)
            self.contribution[self.current] = new
        return

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        return

    def handle_data(self, data):
        # Ignore all the instructions:
        if "Instructions:" in data:
            if self.vb: print("Ignoring the ", data)
            return

        # Check the Program Code:
        if "Program Code:" in data[0:20]:
            THIS_PROGRAM_CODE = data.split(":")[1][1:]
            if THIS_PROGRAM_CODE != self.PROGRAM_CODE:
                raise ValueError('Unexpected Program Code '+THIS_PROGRAM_CODE)
            if self.vb: print("Confirmed Program Code: ", THIS_PROGRAM_CODE)

        # Extract the Personnel information:
        if "Key Personnel:" in data[0:20]:
            self.directory = inkind.Directory()
            return

        # Get key personnel info from the preamble:
        if self.preamble:
            if self.directory is not None:
                self.directory.read(data)
            return

        # Extend the current contribution with whatever text was found:
        self.contribution[self.current].read(data)

        return
