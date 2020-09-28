import requests
from html.parser import HTMLParser

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
            print(self.PROGRAM_CODE+"-"+self.contribution[S].ID+",",
                  ",,",
                  '"'+self.contribution[S].TITLE+'"'+",",
                  self.contribution[S].URL+",",
                  self.contribution[S].LEAD+",",
                  self.contribution[S].EMAIL+",",
                  self.contribution[S].LOI_CODE+",",
                  self.contribution[S].CATEGORY+",",
                  self.contribution[S].RECIPIENTS+",",
                  '"'+self.contribution[S].one_line_SOW()+'"'+",",
                  str(self.contribution[S].VALUE)+",",
                  self.contribution[S].EXCEPTION)
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
            self.directory = Directory()
            return

        # Get key personnel info from the preamble:
        if self.preamble:
            if self.directory is not None:
                self.directory.read(data)
            return

        # Extend the current contribution with whatever text was found:
        self.contribution[self.current].read(data)

        return

# ======================================================================

class Contribution():
    def __init__(self, vb=False):
        self.vb = vb
        self.current = None
        self.ID = None
        self.URL = None
        self.TITLE = None
        self.EXCEPTION = None
        self.LOI_CODE = None
        self.LEAD = None
        self.EMAIL = None
        self.RECIPIENTS = None
        self.VALUE = None
        self.CATEGORY = None
        self.text = {}
        return

    def read(self, data):
        # Get the contribution title:
        if "TITLE:" in data[0:20]:
            self.TITLE = ":".join(data.split(":")[1:])[1:]
            if self.vb: print("    Contribution Title: ", self.TITLE)
            return
        # Check for exception requests. Format: "Exception requested: please begin review on November 6"
        if "Exception requested:" in data[0:20]:
            request = data.split(":")[1][1:]
            self.EXCEPTION = " ".join(request.split(" ")[-2:])
            if self.vb: print("    Contribution Due Date: ", self.EXCEPTION)
            return
        # Get the LOI Code:
        if "LOI Code:" in data[0:20]:
            self.LOI_CODE = data.split(":")[1][1:]
            if self.vb: print("    Contribution LOI Code: ", self.LOI_CODE)
            return
        # Get the Contribution Lead:
        if "Contribution Lead:" in data[0:20]:
            self.LEAD = data.split(":")[1][1:]
            if self.vb: print("    Contribution Lead: ", self.LEAD)
            return
        # Get the Contribution Recipients:
        if "Contribution Recipients:" in data[0:40]:
            self.RECIPIENTS = data.split(":")[1][1:]
            if self.vb: print("    Contribution Recipients: ", self.RECIPIENTS)
            # The recipients are the last thing of interest in the section, so ignore everything else from here.
            self.current = None
            return
        # Ignore the main subsection headings:
        if "PLANNED ACTIVITIES" in data: return
        if "TECHNICAL OBJECTIVES" in data: return
        if "EXPECTED RIGHTS" in data: return
        if "KEY PERSONNEL" in data: return
        # Set the current subsection:
        if "Background: Description" in data:
            self.current = "BACKGROUND_DESCRIPTION"
            self.text[self.current] = ""
            return
        if "Background: One" in data:
            self.current = "BACKGROUND_SUMMARY"
            self.text[self.current] = ""
            return
        if "Activity: Description" in data:
            self.current = "ACTIVITY_DESCRIPTION"
            self.text[self.current] = ""
            return
        if "Activity: One" in data:
            self.current = "ACTIVITY_SUMMARY"
            self.text[self.current] = ""
            return
        if "Deliverables: Description" in data:
            self.current = "DELIVERABLES_DESCRIPTION"
            self.text[self.current] = ""
            return
        if "Deliverables: One" in data:
            self.current = "DELIVERABLES_SUMMARY"
            self.text[self.current] = ""
            return
        if "Deliverables: Timeline" in data:
            self.current = "DELIVERABLES_TIMELINE"
            self.text[self.current] = ""
            return
        if "Data Rights: Description" in data:
            self.current = "DATA_RIGHTS_DESCRIPTION"
            self.text[self.current] = ""
            return
        if "Data Rights: One" in data:
            self.current = "DATA_RIGHTS_SUMMARY"
            self.text[self.current] = ""
            return
        # Now append the data chunk:
        if self.current is not None:
            self.text[self.current] = self.text[self.current] + data
            return

    def print_SOW(self):
        print("Title: "+self.TITLE)
        print("Background: "+self.text["BACKGROUND_SUMMARY"])
        print("Activities: "+self.text["ACTIVITY_SUMMARY"])
        print("Deliverables: "+self.text["DELIVERABLES_SUMMARY"])
        print("Data Rights: "+self.text["DATA_RIGHTS_SUMMARY"])
        print("Contribution Lead: "+str(self.LEAD))
        print("Contribution Recipients: "+str(self.RECIPIENTS))
        return

    def one_line_SOW(self):
        return "Background: "+self.text["BACKGROUND_SUMMARY"] + \
               " Activities: "+self.text["ACTIVITY_SUMMARY"] + \
               " Deliverables: "+self.text["DELIVERABLES_SUMMARY"] + \
               " Data Rights: "+self.text["DATA_RIGHTS_SUMMARY"]
        return

    def extract_PI_value(self):
        N = []
        for word in self.text["DATA_RIGHTS_SUMMARY"].split():
             try:
                 N.append(float(word))
             except ValueError:
                 pass
        # Return integer if possible:
        if int(N[0]) == int(round(N[0])):
            self.VALUE = int(N[0])
        else:
            self.VALUE = N[0]
        return self.VALUE

    def estimate_category(self):
        self.CATEGORY = "Unknown"
        if "ataset" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "1.1 - Old complementary dataset"
            if "dded" in self.text["ACTIVITY_SUMMARY"]:
                self.CATEGORY = "1.2 - Reprocessed/analyzed LSST data"
            if "arget" in self.text["ACTIVITY_SUMMARY"]:
                self.CATEGORY = "1.3 - New complementary targeted data"
            if "urvey" in self.text["ACTIVITY_SUMMARY"]:
                self.CATEGORY = "1.4 - New complementary survey"
        if "Full IDAC" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "2.1 - Full IDAC"
        if "Lite IDAC" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "2.2 - Lite IDAC"
        if "Scientific Processing Center" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "2.3 - Computing resources for SCs"
        if "elescope time" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "3.1 - Open telescope time"
        if "ollow-up" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "3.2 - Active Follow-up Program"
        if "directable" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "4.2 - Directable SW dev"
        if "non-directable" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "4.3 - Non-directable SW dev"
        if "eneral pool" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "4.1 - General pooled SW dev"
        if "onstruction" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "5.1 - Construction"
        if "ommissioning" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "5.2 - Commissioning"
        if "ffset" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "5.3 - Operations Cost Offset"
        if "nhancement" in self.text["ACTIVITY_SUMMARY"]:
            self.CATEGORY = "5.4 - Non-SW Facility Enhancement"
        return self.CATEGORY

    def match_email(self, directory):
        surname = self.LEAD.split()[-1]
        for name in directory.people:
            if surname in name:
                self.EMAIL = directory.people[name]["EMAIL"]
        return self.EMAIL

# ======================================================================

class Directory():
    def __init__(self, vb=False):
        self.vb = vb
        self.current_person = None
        self.current_field = None
        self.people = {}
        return

    def read(self, data):
        # Get the role and name, and start a new person:
        if "Lead:" in data or "Manager:" in data:
            new = {}
            new["ROLE"] = data.split(":")[0]
            sentence = ":".join(data.split(":")[1:])[1:]
            new["NAME"] = sentence.split(",")[0]
            self.current_person = new["NAME"]
            self.people[self.current_person] = new
            return
        # Read the email or address and add it to the new Person
        if "Email:" in data:
            self.current_field = "EMAIL"
            self.people[self.current_person][self.current_field] = ""
        if "Address:" in data:
            self.current_field = "ADDRESS"
            self.people[self.current_person][self.current_field] = ""
        if "Abstract" in data:
            self.current_field = None
        # Clean up the current data chunk:
        clean = data.replace("Email: ","").replace("Address: ","").replace("\xa0","")
        # Append the current data chunk to the current field:
        if self.current_field is not None:
            self.people[self.current_person][self.current_field] = self.people[self.current_person][self.current_field] + clean
        # print("Current person: ", self.people[self.current_person])
        return

# ======================================================================

gdoc = {}
# Proposal Template:
# gdoc["BUL-NAO"] = "https://docs.google.com/document/d/1NDnIvLaiJ9PRXGFwVmU9aMQaqJWnNstAqNUjPUoduio/edit"
# NED-UTR:
gdoc["NED-UTR"] = "https://docs.google.com/document/d/18_5hLK6vtHqDM2q5BfTdoaFB8C2Ait_JZzzbhCiy59E/edit"

proposal = {}
for program in gdoc:
    proposal[program] = Proposal(program, gdoc[program], vb=False)
    proposal[program].download()
    proposal[program].read()
    proposal[program].print_csv()
    # proposal[program].print_SOW()
