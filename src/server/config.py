# Simple python file that defines globals for the flask server.
#
#   Connor Shugg

import os

# Server globals
server_addr = "0.0.0.0"
server_port = 7669
server_root_dpath = "/home/ugrads/nonmajors/cwshugg/personal/snowbudget/root"
server_home_fname = "index.html"            # home page for non-auth users
server_home_auth_fname = "auth/index.html"  # home page for auth users
server_public_files = [server_home_fname, "auth.js", "main.css", "favicon.ico"]

# Budget globals
sb_config_fpath = "/home/ugrads/nonmajors/cwshugg/personal/snowbudget/config/example.json"

# Authentication globals
key_dpath = "/home/ugrads/nonmajors/cwshugg/personal/snowbudget/keys"
auth_key_fname = "auth_password.key"
auth_jwt_key_fname = "auth_jwt.key"

# Certifications/OpenSSL globals
certs_enabled = False
certs_dpath = "TODO"
certs_cert_fname = "TODO"
certs_key_fname = "TODO"

