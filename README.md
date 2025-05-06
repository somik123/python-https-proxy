# python-https-proxy
Simple https proxy script written in python

## Create SSL certificates
Run the following command and follow the steps to create a key file. Remember the pass phrase you use.
```
openssl genrsa -aes256 -out key.pem
```

Run the following command and follow the steps to create the certificate file. Use the same pass phrase you used in the previous step.
```
openssl req -new -x509 -key key.pem -out cert.pem -days 1095
```

Edit the `proxy.py` file and provide the pass phrase as the password on line 12.

Place all 3 files in the same directory and run the script:
`python3 proxy.py`

> Note: <br>
> Change the port on line 7 to something else. <br>
> If you want the proxy to be available only to the localhost, change the host on line 6 to localhost or 127.0.0.1