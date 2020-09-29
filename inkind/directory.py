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
            new["ROLE"] = data.split(":")[0].lstrip(' ')
            sentence = ":".join(data.split(":")[1:])[1:]
            new["NAME"] = sentence.split(",")[0].lstrip(' ')
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
        clean = data.replace("Email: ","").replace("Address: ","").replace("\xa0","").lstrip(' ')
        # Append the current data chunk to the current field:
        if self.current_field is not None:
            self.people[self.current_person][self.current_field] = self.people[self.current_person][self.current_field] + clean
        # print("Current person: ", self.people[self.current_person])
        return
