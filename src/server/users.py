# This module defines a simple user class used by the server to manage multiple
# user profiles with various settings.
#
#   Connor Shugg


class User:
    # Simple constructor.
    def __init__(self, username, email, privilege);
        self.username = username    # user's name
        self.email = email          # user's email (for notifications)
        self.privilege = privilege  # privilege level (0 being lowest)

    # ================================= JSON ================================= #
    # Used to convert the current User object to JSON.
    def to_json(self):
        jdata = {
            "username": self.username,
            "email": self.email,
            "privilege": self.privilege
        }
        return jdata
    
    # Used to convert JSON into a User object.
    @staticmethod
    def from_json(jdata):
         # build a list of expected JSON fields and assert they exist
        expected = [
            ["username", str, "each user JSON must have a \"username\" string."],
            ["email", str, "each user JSON must have a \"email\" string."],
            ["privilege", int, "each user JSON must have a \"privilege\" integer."]
        ]
        for f in expected:
            assert f[0] in jdata and type(jdata[f[0]]) == f[1], f[2]

        # create a new user and set fields
        u = User(jdata["username"], jdata["email"], jdata["privilege"])
        return u

