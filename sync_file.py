##
# @file sync_file.py
# @brief Implement syncing of files over the internet.
# @author cwee

import base64
import urllib.request
from threading import Timer


class WebDAVFsync:
    def __init__(self, url, local_fpath, username, password, interval=None,
            callback=None):
        self.url = url
        self.local_fpath = local_fpath
        userpass = "{}:{}".format(username, password).encode()
        self.auth_b64 = base64.b64encode(userpass).decode("ascii")

        self.last_hash = None
        self.set_callback(callback)
        self.thread = None

        if interval is not None:
            interval = float(interval)
            if interval < 0:
                raise ValueError("Invalid sync interval specified")
            self.continuous_sync(interval * 60)  # convert min to sec

    def set_callback(self, callback):
        if callback is None:
            self.callback = lambda *args: None
        else:
            self.callback = callback

    def upload(self):
        with open(self.local_fpath, "rb") as upload_f:
            file_data = upload_f.read()
        self.last_hash = hash(file_data)

        put_req = urllib.request.Request(
            url=self.url,
            data=file_data,
            headers={"Authorization": "Basic {}".format(self.auth_b64)},
            method="PUT",
        )
        with urllib.request.urlopen(put_req) as url_req:
            pass

        return url_req

    ##
    # @brief Fetch file from server without saving it to the local path.
    def fetch(self):
        get_req = urllib.request.Request(
            url=self.url,
            headers={"Authorization": "Basic {}".format(self.auth_b64)},
            method="GET",
        )
        with urllib.request.urlopen(get_req) as url_req:
            file_data = url_req.read()

        return url_req, file_data

    def download(self):
        url_req, file_data = self.fetch()
        with open(self.local_fpath, "wb") as download_f:
            download_f.write(file_data)

        return url_req

    ##
    # @brief Check for changes to file at specified interval.
    # @note Does not update file on disk.
    def continuous_sync(self, interval):
        _, peek_data = self.fetch()
        curr_hash = hash(peek_data)
        if curr_hash != self.last_hash:
            self.last_hash = curr_hash
            self.callback(peek_data)

        self.thread = Timer(interval, lambda: self.continuous_sync(interval))
        self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.thread.cancel()
