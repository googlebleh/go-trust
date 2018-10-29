##
# @file sync_file.py
# @brief Implement syncinc of files over the internet.
# @author cwee


import base64
import urllib.request


class WebDAVFsync:
    def __init__(self, url, local_fpath, username, password):
        self.url = url
        self.local_fpath = local_fpath
        userpass = "{}:{}".format(username, password).encode()
        self.auth_b64 = base64.b64encode(userpass).decode("ascii")

    def upload(self):
        with open(self.local_fpath, "rb") as upload_f:
            file_data = upload_f.read()

        put_req = urllib.request.Request(
            url=self.url,
            data=file_data,
            headers={"Authorization": "Basic {}".format(self.auth_b64)},
            method="PUT",
        )
        with urllib.request.urlopen(put_req) as url_req:
            pass

        return url_req

    def download(self):
        get_req = urllib.request.Request(
            url=self.url,
            headers={"Authorization": "Basic {}".format(self.auth_b64)},
            method="GET",
        )
        with urllib.request.urlopen(get_req) as url_req:
            file_data = url_req.read()

        with open(self.local_fpath, "wb") as download_f:
            download_f.write(file_data)

        return url_req
