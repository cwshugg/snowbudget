FROM python:3.8-alpine
# These are the same commands as from /scripts/get-dependencies.sh
RUN pip install --user -U pip setuptools 
RUN pip install requests
RUN pip install Flask
RUN pip uninstall JWT
RUN pip uninstall PyJWT
RUN pip install PyJWT
RUN pip install install openpyxl
# Copy over data as requested
COPY ./scripts /scripts
COPY ./root /root
COPY ./src /src
COPY ./config /config
# Run the make-links.sh
RUN ln -sf /src/cli/main.py /sb
RUN ln -sf /src/server/main.py /sbserv
# Run the server
CMD  python /src/server/main.py /config/server-example.json