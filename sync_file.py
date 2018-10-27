#!/usr/bin/env python3

# for https_get
from http.client import HTTPSConnection
from base64 import b64encode

# for https_put
import urllib.request


def https_get():
    #This sets up the https connection
    c = HTTPSConnection("dav.box.com")
    #we need to base 64 encode it 
    #and then decode it to acsii as python 3 stores it as a byte string
    userAndPass = b64encode(b"user@email.com:password").decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass }
    #then connect
    c.request('GET', '/dav/path/to/hello.txt', headers=headers)
    #get the response back
    res = c.getresponse()
    # at this point you could check the status etc
    # this gets the page text
    data = res.read()  
    print(data)


def https_put():
    with open("go_board.pickle", "rb") as f:
        file_data = f.read()

    req = urllib.request.Request(
        url="https://dav.box.com/dav/path/to/goboard.pickle",
        data=file_data,
        method="PUT"
    )
    userAndPass = b64encode(b"user@email.com:password").decode("ascii")
    req.add_header("Authorization", "Basic %s" % userAndPass)
    with urllib.request.urlopen(req) as f:
        pass

    print("Status", f.status)
    print("Reason", f.reason)


if __name__ == "__main__":
    https_put()
