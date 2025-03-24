#! /bin/bash -

# Create a directory for certificates
mkdir certs
cd certs

# Generate a private key
openssl genrsa -out server.key 2048

# Generate a certificate signing request (CSR)
openssl req -new -key server.key -out server.csr

# Generate a self-signed certificate valid for 1 year
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
