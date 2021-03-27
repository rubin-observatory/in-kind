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
            new["ROLE"] = data.split(":")[0].strip().replace("\xa0","")
            sentence = ":".join(data.split(":")[1:])[1:]
            new["NAME"] = sentence.split(",")[0].strip().replace("\xa0","")
            # print("NAME check:",new["NAME"]," extracted from data:",data)
            self.current_person = new["NAME"]
            self.people[self.current_person] = new
            return
        # Read the email or address and add it to the new Person
        elif "Email:" in data:
            self.current_field = "EMAIL"
            self.people[self.current_person][self.current_field] = ""
        elif "Address:" in data:
            self.current_field = "ADDRESS"
            self.people[self.current_person][self.current_field] = ""
        else:
            self.current_field = None
        # Clean up the current data chunk:
        clean = data.replace("Email: ","").replace("Address: ","").replace("\xa0","").strip()
        # if self.current_field == "EMAIL":
        #     print("    Email addressee = ",self.current_person)
        #     print("    Email data = ",data)
        #     print("    Cleaned Email data = ",clean)
        # Append the current data chunk to the current field:
        if self.current_field is not None:
            self.people[self.current_person][self.current_field] = self.people[self.current_person][self.current_field] + clean
        # print("Current person: ", self.people[self.current_person])
        return
