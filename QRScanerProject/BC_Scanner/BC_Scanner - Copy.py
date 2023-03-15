"""
*Important libraries*
#pip install opencv-python
#pip install pyzbar
#pip install watchdog
#pip install numpy

Scan condition
- sacn only first page
- file format = .jpg, .png, .tiff, .pdf
- QR type = CODE39
- only 1 QR code
"""

import cv2
from pyzbar.pyzbar import decode
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os
from threading import Thread
from multiprocessing import Queue


class SqlLoaderWatchdog(PatternMatchingEventHandler):
    def __init__(self, queue, patterns):
        PatternMatchingEventHandler.__init__(self, patterns=patterns)
        self.queue = queue

    def process(self, event):
        self.queue.put(event)

    def on_created(self, event):
        self.process(event)

def Readbarcode(image):
    haveQR = False
    output = ''
    qr_count = 0
    detectedbarcodes = ''
    while True:
        try:
            img = cv2.imread(image)
            detectedbarcodes = decode(img)
        except Exception as error:
            print("error while reading barcode and retrying")
            time.sleep(1)
            continue
        break

    if not detectedbarcodes:
        print("Error: not detected barcode")
    else:
        for barcode in detectedbarcodes:
            if barcode.type == "CODE39":
                if barcode.data != "":
                    qr_count += 1
                    if qr_count > 1:
                        print("error: this file has more than 1 QR")
                        break
                    else:
                        output = (str(barcode.data).lstrip("b'").rstrip("'") + '_')
        haveQR = True
    return output if haveQR and qr_count == 1 else "ERROR_"


def process_load_queue(q):
    while True:
        if not q.empty():
            event = q.get()
            scan_file(event.src_path)
        else:
            time.sleep(1)


def scan_file(filepath):
    if filepath[-3:] == "tif" or filepath[-4:] == "tiff":
        print(
            "----------------------------------------------------------------------------"
            "---------------------------------\nDetected " + filepath.split('\\')[-1])
        oldname = filepath
        newname = f"temp\\Reading." + oldname.split(".")[-1]
        while True:
            try:
                os.rename(oldname, newname)
            except:
                print("error while moving file to temp and retrying")
                time.sleep(1)
                continue
            break

        while True:
            try:
                os.rename(newname,
                          scan_path + '\\' + post_path + '\\' + str(Readbarcode(newname)) + oldname.lstrip(
                              scan_path + '\\'))
            except:
                print("error while reading and moving file to imgOut and retrying")
                time.sleep(1)
                continue
            break
    print("Finished scanning the file.")


if __name__ == '__main__':
    temp_path = "temp"  # set temp file path
    scan_path = "img"  # set scan file path
    post_path = "imgOut" # set scanned file path

    for f in os.listdir(temp_path):
        print("Clearing old temp")
        os.remove(os.path.join(temp_path, f))

    for of in os.listdir(scan_path):
        oldfile = os.path.join(scan_path, of)
        if os.path.isdir(oldfile):
            continue
        else:
            scan_file(oldfile)

    # create queue
    watchdog_queue = Queue()

    # Set up a worker thread to process database load
    worker = Thread(target=process_load_queue, args=(watchdog_queue,))
    worker.daemon = True
    worker.start()

    # setup watchdog to monitor directory for trigger files
    patterns = ["*"]
    event_handler = SqlLoaderWatchdog(watchdog_queue, patterns=patterns)
    observer = Observer()
    observer.schedule(event_handler, path=scan_path)
    observer.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# TGOD
