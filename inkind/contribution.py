import sys

# ======================================================================

class Contribution():
    def __init__(self, vb=False, program=None):
        self.vb = vb
        self.PROGRAM_CODE = program
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
        # Check the contribution ID:
        if "Statement of Work and Detailed Plan" in data:
            THIS_ID = data.split(".")[0].strip()
            if THIS_ID != self.ID[8:11]:
                print("    WARNING: Modifying contribution ID to match value in proposal "+self.PROGRAM_CODE+". Proposal value cf sequential ID: ", THIS_ID, self.ID[8:11],"New ID:",self.PROGRAM_CODE+"-"+THIS_ID, file=sys.stderr)
                self.ID = self.PROGRAM_CODE+"-"+THIS_ID
            return
        # Get the contribution title:
        if "TITLE:" in data[0:20]:
            if self.vb: print("    Data: ", data[0:20])
            self.TITLE = ":".join(data.split(":")[1:])[1:].strip()
            if self.vb: print("    Contribution Title: ", self.TITLE)
            return
        # Check for exception requests. Format: "Exception requested: please begin review on November 6"
        if "Exception requested:" in data[0:20]:
            request = data.split(":")[1][1:]
            self.EXCEPTION = " ".join(request.split(" ")[-2:]).strip()
            if self.vb: print("    Contribution Due Date: ", self.EXCEPTION)
            return
        # Get the LOI Code:
        if "LOI Code:" in data[0:20]:
            self.LOI_CODE = data.split(":")[1][1:].strip()
            if self.vb: print("    Contribution LOI Code: ", self.LOI_CODE)
            return
        # Get the Contribution Lead:
        if "Contribution Lead:" in data[0:20]:
            self.LEAD = data.split(":")[1][1:].strip()
            if self.vb: print("    Contribution Lead: ", self.LEAD)
            return
        # Get the Contribution Recipients:
        if "Contribution Recipients:" in data[0:40]:
            self.RECIPIENTS = data.split(":")[1][1:].strip()
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
            self.text[self.current] = self.text[self.current] + data.replace('"',"'")
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
        try:
            line = "Background: "+self.text["BACKGROUND_SUMMARY"] + \
               " Activities: "+self.text["ACTIVITY_SUMMARY"] + \
               " Deliverables: "+self.text["DELIVERABLES_SUMMARY"] + \
               " Data Rights: "+self.text["DATA_RIGHTS_SUMMARY"]
        except:
            line = "Not yet available"
        return line

    def extract_PI_value(self):
        try:
            N = []
            for word in self.text["DATA_RIGHTS_SUMMARY"].split():
                try:
                    N.append(float(word))
                except ValueError:
                    pass
            # Return integer if possible:
            if int(N[0]) == int(round(N[0]+0.01)):
                self.VALUE = int(N[0])
            else:
                self.VALUE = N[0]
        except:
            self.VALUE = "Not yet available"
        return self.VALUE

    def estimate_category(self):
        try:
            self.CATEGORY = "Unknown"
            if "ataset" in self.text["ACTIVITY_SUMMARY"]:
                self.CATEGORY = "1.1 - Old complementary dataset"
                if "dded" in self.text["ACTIVITY_SUMMARY"]:
                    self.CATEGORY = "1.2 - Reprocessed/analyzed LSST data"
                if "arget" in self.text["ACTIVITY_SUMMARY"]:
                    self.CATEGORY = "1.3 - New complementary targeted data"
                if "urvey" in self.text["ACTIVITY_SUMMARY"]:
                    self.CATEGORY = "1.4 - New complementary survey"
            if "IDAC" in self.text["ACTIVITY_SUMMARY"]:
                self.CATEGORY = "2.2 - Lite IDAC"
            if "Full IDAC" in self.text["ACTIVITY_SUMMARY"]:
                self.CATEGORY = "2.1 - Full IDAC"
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
        except:
            self.CATEGORY = "Not yet available"
        return self.CATEGORY

    def match_email(self, directory):
        # print(directory.people)
        if self.LEAD is None:
            self.EMAIL = None
        else:
            # Attempt to extract their surname
            # print("self.LEAD = ",self.LEAD)
            surname = self.LEAD.split()[-1]
            for name in directory.people:
                if surname in name:
                    self.EMAIL = directory.people[name]["EMAIL"]
        return self.EMAIL
