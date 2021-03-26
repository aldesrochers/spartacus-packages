# =============================================================================
# Copyright (C) 2021-
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# Alexis L. Desrochers (alexisdesrochers@gmail.com)
#
# =============================================================================

import os, requests
from conans import tools


def download(file_id, filename, sha256=""):
    """
    Download a file from google drive.
    :param file_id: Unique file id on google drive.
    :param filename: Filename of the file on disk,
    :param sha256: File hash.
    :return:
    """

    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        print("Downloading {} from Google Drive.".format(filename))
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)
    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)
    save_response_content(response, filename)
    # check sha256 signature
    if len(sha256) > 0:
        tools.check_sha256(filename, sha256)

def get(file_id, filename, sha256=""):
    """
    Wrapper used to get a file from google drive.
    :param file_id: Unique file id on google drive.
    :param filename: Filename of the file on disk,
    :param sha256: File hash.
    :return:
    """
    if os.path.exists(filename):
        raise Exception("File already exists {}".format(filename))
    download(file_id, filename, sha256)
    tools.untargz(filename)
    os.remove(filename)







if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__))
    fname = os.path.join(path, "opencascade-7.5.0.tgz")
    file_id = "1kkPvtvv-3wZzF036WdiuSnGpljfIBsLE"
    filename = fname
    googledrive_get(file_id, fname)

    print(os.getcwd())