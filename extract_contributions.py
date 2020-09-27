import requests
from html.parser import HTMLParser

class ProposalParser(HTMLParser):

    def __init__(self, url, vb=False):
        super().__init__()
        self.gdoc = url
        self.vb = vb
        self.htmlfile = "proposal.html"
        self.preamble = True
        self.PROGRAM_CODE = None
        self.count = 0
        self.ID = []
        self.URL = []
        self.TITLE = []
        self.LOI_CODE = []
        return

    def download(self):
        html = self.gdoc.replace("edit", "export?format=html")
        if self.vb: print("Downloading Gdoc as HTML via ",html)
        r = requests.get(html, allow_redirects=True)
        open(self.htmlfile, 'wb').write(r.content)
        if self.vb: print("New HTML file: ", self.htmlfile)
        return

    def run(self):
        f = open(self.htmlfile, 'r')
        self.feed(f.read())
        f.close()
        return

    def report(self):
        if self.vb: print("Extracted ",self.count," contributions:")
        for k in range(self.count):
            print(self.PROGRAM_CODE+"-"+self.ID[k]+",",
                  '"'+self.TITLE[k]+'"'+",",
                  self.URL[k]+",",
                  self.LOI_CODE[k])
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
            self.ID.append("S"+str(self.count))
            if self.vb: print("    Contribution ID: ", self.ID[-1])
            for attr in attrs:
                # print("     attr:", attr)
                if attr[0] == "id": heading = attr[1]
            self.URL.append(self.gdoc + "#heading=" + heading)
            if self.vb: print("    Contribution section URL: ", self.URL[-1])
        return

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        return

    def handle_data(self, data):
        # Ignore all the instructions:
        if data[0:12] != "Instructions":
            if self.vb: print("Encountered some text: ", data)
            pass

        # Get the Program Code:
        if "Program Code" in data[0:12]:
            self.PROGRAM_CODE = data.split(":")[1][1:]
            if self.vb: print("Program Code: ", self.PROGRAM_CODE)

        if self.preamble: return

        # Get the contribution title:
        if "TITLE" in data[0:12]:
            title = ":".join(data.split(":")[1:])[1:]
            self.TITLE.append(title)
            if self.vb: print("    Contribution Title: ", self.TITLE[-1])
        # Get the LOI Code:
        if "LOI Code" in data[0:12]:
            self.LOI_CODE.append(data.split(":")[1][1:])
            if self.vb: print("    Contribution LOI Code: ", self.LOI_CODE[-1])
        return

# ======================================================================

gdoc = "https://docs.google.com/document/d/1NDnIvLaiJ9PRXGFwVmU9aMQaqJWnNstAqNUjPUoduio/edit"

parser = ProposalParser(gdoc, vb=False)
parser.run()
parser.report()
