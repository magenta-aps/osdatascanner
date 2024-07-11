#!/bin/bash

set -ex

here=$(dirname "$0")

get_tesseract_models() {
    mkdir -p "$here/downloads/tessdata"
    pushd "$here/downloads/tessdata"
    curl --location -o mrz.traineddata \
        https://github.com/DoubangoTelecom/tesseractMRZ/raw/master/tessdata_best/mrz.traineddata
}

get_tesseract_models

get_os2kle_model() {
    mkdir -p "$here/downloads/os2kledata"
    pushd "$here/downloads/os2kledata"
    curl --loadtion -o OS2KLE.json \
        "https://github.com/os2kle/os2kle/blob/master/OS2KLE.json"
}

get_os2kle_model
