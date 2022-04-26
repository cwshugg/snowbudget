# Simple python file that defines configurations for the flask server.
#
#   Connor Shugg

# Imports
import os
import json

# Local imports
from users import User

# Main config class.
class Config:
    def __init__(self, fpath):
        self.fpath = fpath

        # open up the file and try to parse it as JSON
        fp = open(fpath, "r")
        data = fp.read()
        fp.close()
        jdata = json.loads(data)

        # now, define and check all fields
        expected = [
            # server-related configs
            ["server_addr", str, "missing server_addr string"],
            ["server_port", int, "missing server_port int"],
            ["server_root_dpath", str, "missing server_root_dpath string"],
            ["server_home_fname", str, "missing server_home_fname string"],
            ["server_home_auth_fname", str, "missing server_home_auth_fname string"],
            ["server_public_files", list, "missing server_public_files list"],
            ["server_secret_key", str, "missing server_secret_key string"],
            # budget-related configs
            ["sb_config_fpath", str, "missing sb_config_fpath string"],
            # key-related configs
            ["auth_key", str, "missing auth_key string"],
            ["auth_jwt_key", str, "missing auth_jwt_key string"],
            # notification-related configs
            ["ifttt_webhook_key", str, "missing ifttt_webhook_key string"],
            ["notif_webhook_event", str, "missing notify_webhook_event string"],
            # certs/HTTPS-related configs
            ["certs_enabled", bool, "missing certs_enabled boolean"],
            ["certs_dpath", str, "missing certs_dpath string"],
            ["certs_cert_fname", str, "missing certs_cert_fname string"],
            ["certs_key_fname", str, "missing certs_key_fname string"],
            # user-related configs
            ["users", list, "missing users list"],
            # renewer thread configs
            ["rthread_tick_rate", int, "missing rthread_tick_rate int"],
            ["rthread_notif_threshold", int, "missing rthread_notif_threshold int"]
        ]

        # for each expected entry, assert its existence then set it as a global
        for f in expected:
            key = f[0]
            assert key in jdata and type(jdata[key]) == f[1], f[2]
            setattr(self, key, jdata[key])

        # for each user, try to create a user object
        uobjs = []
        for udata in self.users:
            uobjs.append(User.from_json(udata))
        self.users = uobjs

