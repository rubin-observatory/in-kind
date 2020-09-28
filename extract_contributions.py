import requests
from html.parser import HTMLParser

class ProposalParser(HTMLParser):

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
        return

    def download(self):
        html = self.gdoc.replace("edit", "export?format=html")
        if self.vb: print("Downloading Gdoc as HTML via ",html)
        r = requests.get(html, allow_redirects=True)
        open(self.htmlfile, 'wb').write(r.content)
        if self.vb: print("New HTML file: ", self.htmlfile)
        return

    def run(self):
        if self.vb: print("Reading proposal from ",self.htmlfile)
        f = open(self.htmlfile, 'r')
        self.feed(f.read())
        f.close()
        return

    def report(self):
        if self.vb: print("Extracted ",self.count," contributions:")
        for S in self.contribution:
            print(self.PROGRAM_CODE+"-"+self.contribution[S].ID+",",
                  '"'+self.contribution[S].TITLE+'"'+",",
                  self.contribution[S].URL+",",
                  self.contribution[S].LOI_CODE+",",
                  self.contribution[S].EXCEPTION)
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
            new = Contribution()
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
        if data[0:12] != "Instructions:":
            if self.vb: print("Encountered some text: ", data)
            pass

        # Get the Program Code:
        if "Program Code:" in data[0:12]:
            THIS_PROGRAM_CODE = data.split(":")[1][1:]
            if THIS_PROGRAM_CODE != self.PROGRAM_CODE:
                raise ValueError('Unexpected Program Code '+THIS_PROGRAM_CODE)
            if self.vb: print("Confirmed Program Code: ", THIS_PROGRAM_CODE)

        if self.preamble: return

        # Get the contribution title:
        if "TITLE:" in data[0:12]:
            title = ":".join(data.split(":")[1:])[1:]
            self.contribution[self.current].TITLE = title
            if self.vb: print("    Contribution Title: ", title)
        # Check for exception requests. Format: "Exception requested: please begin review on November 6"
        if "Exception requested:" in data[0:20]:
            request = data.split(":")[1][1:]
            due_date = " ".join(request.split(" ")[-2:])
            self.contribution[self.current].EXCEPTION = due_date
            if self.vb: print("    Contribution Due Date: ", due_date)        # Get the LOI Code:
        if "LOI Code:" in data[0:12]:
            self.contribution[self.current].LOI_CODE = data.split(":")[1][1:]
            if self.vb: print("    Contribution LOI Code: ", self.contribution[self.current].LOI_CODE)
        return

# ======================================================================

class Contribution():
    def __init__(self):
        self.ID = None
        self.URL = None
        self.TITLE = None
        self.EXCEPTION = None
        self.LOI_CODE = None
        return

# ======================================================================

gdoc = {}
# Proposal Template:
# gdoc["BUL-NAO"] = "https://docs.google.com/document/d/1NDnIvLaiJ9PRXGFwVmU9aMQaqJWnNstAqNUjPUoduio/edit"
# NED-UTR:
gdoc["NED-UTR"] = "https://docs.google.com/document/d/18_5hLK6vtHqDM2q5BfTdoaFB8C2Ait_JZzzbhCiy59E/edit"

proposal = {}
for program in gdoc:
    proposal[program] = ProposalParser(program, gdoc[program], vb=True)
    proposal[program].download()
    proposal[program].run()
    proposal[program].report()
