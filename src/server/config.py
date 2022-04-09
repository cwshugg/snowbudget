# Simple python file that defines globals for the flask server.
#
#   Connor Shugg

import os

# Server globals
server_addr = "0.0.0.0"
server_port = 7669
server_root_dpath = "/home/snowmiser/snowbudget/root"
server_home_fname = "index.html"            # home page for non-auth users
server_home_auth_fname = "auth_index.html"  # home page for auth users
server_public_files = [server_home_fname, "script/auth.js", "assets/main.css", "assets/favicon.ico"]

# Budget globals
sb_config_fpath = "/home/snowmiser/snowbudget/config/example.json"

# Authentication globals
key_dpath = "/home/snowmiser/snowbudget/keys"
auth_key_fname = "auth_password.key"
auth_jwt_key_fname = "auth_jwt.key"

# Certifications/OpenSSL globals
certs_enabled = True
certs_dpath = "/etc/letsencrypt/live/beacon.shugg.dev/"
certs_cert_fname = "fullchain.pem"
certs_key_fname = "privkey.pem"

