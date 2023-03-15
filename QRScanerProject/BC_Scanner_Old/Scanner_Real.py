"""
*Important libraries*
#pip install pdf2image
#pip install opencv-python
#pip install pyzbar
#pip install watchdog
#pip install numpy
"""

import cv2
from pyzbar.pyzbar import decode
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from pdf2image import convert_from_path
import os
from threading import Thread
from multiprocessing import Queue
from PIL import ImageEnhance
from PIL import Image

class SqlLoaderWatchdog(PatternMatchingEventHandler):
    def __init__(self, queue, patterns):
        PatternMatchingEventHandler.__init__(self, patterns=patterns)
        self.queue = queue

    def process(self, event):
        self.queue.put(event)

    def on_created(self, event):
        self.process(event)

def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        print(c)
        return 128 + factor * (c - 128)

    return img.point(contrast)


def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # COLOR_BGR2HSV
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


def Readbarcode(image, oldname):
    output = ''
    print("Reading " + oldname)
    img = cv2.imread(image)
    haveQR = False

    print("enhance")
    gray2 = Image.fromarray(img)
    contrast = ImageEnhance.Contrast(gray2)
    contrast_applied = contrast.enhance(10)

    # cv2.imshow("Image", img[i])
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    detectedbarcodes = decode(contrast_applied)

    if not detectedbarcodes:
        print("Not Detected")
    else:
        print("Writing CSV file.")
        qr_count = 0
        image_path = oldname.split(".")
        image_name = oldname.lstrip(path + '\\')
        for barcode in detectedbarcodes:
            qr_count += 1
            if barcode.data != "":
                output = ('H_' + str(barcode.data).lstrip("b'").rstrip("'") + '_')
        haveQR = True
    return output if haveQR else "Hx_"


def process_load_queue(q):
    exception = ["Reading", "ReadError", "NotDetected", "Done", "H", "Hx"]
    while True:
        if not q.empty():
            event = q.get()
            if (exception[0] not in event.src_path) and (exception[1] not in event.src_path) and (
                    exception[2] not in event.src_path) and (exception[3] not in event.src_path) and (
                    exception[4] not in event.src_path) and (exception[5] not in event.src_path) and (
                    event.src_path[-3:] != "csv") and "." in event.src_path[-4:]:
                print(
                    "----------------------------------------------------------------------------"
                    "---------------------------------\nDetected " + event.src_path)
                oldname = event.src_path
                # newname = "temp\\" + "Reading_" + oldname.lstrip(path + '\\')
                newname = f"temp\\Reading." + oldname.split(".")[-1]
                if oldname[-3:] == "pdf":
                    newpng = (newname.rstrip(".pdf"))
                    print("Converting pdf to png.")
                    page = convert_from_path(oldname, 500, poppler_path=r"Libs\poppler\Library\bin")
                    page[0].save(newpng + '.jpg', 'JPEG')
                    # print("Tranfering to temp.")
                    os.rename(oldname, newname)
                    os.rename(newname,
                              path + '\\' + Readbarcode(newpng + ".jpg", oldname) + oldname.lstrip(path + '\\'))
                    os.remove(newpng + ".jpg")
                else:
                    # print("Tranfering to temp.")
                    os.rename(oldname, newname)
                    os.rename(newname, path + '\\' + str(Readbarcode(newname, oldname)) + oldname.lstrip(path + '\\'))
                print("Finished reading the file.")
        else:
            time.sleep(1)


if __name__ == '__main__':
    dir = 'temp' # set temp file path
    path = "img"  # set scan path
    
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

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
    observer.schedule(event_handler, path=path)
    observer.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
