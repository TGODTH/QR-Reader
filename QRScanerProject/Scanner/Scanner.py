"""
*Important libraries*
#pip install pdf2image
#pip install opencv-python
#pip install pyzbar
#pip install watchdog
#pip install python-poppler
"""
import cv2
from pyzbar.pyzbar import decode
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import csv
from pdf2image import convert_from_path
import os
import numpy as np


# Make one method to decode the barcode
def BarcodeReader(image):
    print("changeing - " + image)
    pdf = False
    image_path = image.split(".")
    image_name = image.lstrip(path + '\\')
    newpath = path + '\\' + 'reading.' + image_path[1]
    if image_path[1] == 'pdf':
        page = convert_from_path(image, 500, poppler_path=r"Libs\poppler\Library\bin")
        page[0].save((image_name.rstrip(".pdf")) + '.jpg', 'JPEG')
        os.rename(image, newpath)
        image = (newpath.rstrip(".pdf")) + '.jpg'
        pdf = True
    else:
        os.rename(image, newpath)
        image = newpath

    # read the image in numpy array using cv2
    print("reading - " + image)
    img = cv2.imread(image)
    qr_count = 0

    # Decode the barcode image
    if image.split(".")[1] != 'pdf' or image.split(".")[1] != 'csv':
        detectedBarcodes = decode(img)

    # If not detected then print the message
    if not detectedBarcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")
        if pdf:
            os.rename(image_path[0] + '.pdf', path + '\\' + 'brNotFound_' + image_name)
            os.remove((image_name.rstrip(".pdf")) + '.jpg')
        else:
            os.rename(image, path + '\\' + 'brNotFound_' + image_name)
    else:

        # Traverse through all the detected barcodes in image
        for barcode in detectedBarcodes:
            qr_count += 1
            # Locate the barcode position in image
            (x, y, w, h) = barcode.rect

            if barcode.data != "":
                # print(barcode.data)
                # print(barcode.type)
                csvheader = ['FileName', 'decodeStatus', 'row', 'BCLocation', 'BCType', 'BCTEXT']
                csvdata = ["read_" + image_name, 1, qr_count, f'{x};{y}', barcode.type, barcode.data]
                with open(f'{image_path[0]}.csv', 'a', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)

                    # write the header
                    if qr_count == 1:
                        writer.writerow(csvheader)

                    # write the data
                    writer.writerow(csvdata)
        if pdf:
            os.rename(image_path[0] + '.pdf', path + '\\' + 'read_' + image_name)
            os.remove((image_name.rstrip(".pdf")) + '.jpg')
        else:
            os.rename(image, path + '\\' + 'read_' + image_name)
        os.rename(f'{image_path[0]}.csv', path + '\\' + 'read_' + image_path[0].lstrip(path + '\\') + '.csv')
        print("read - " + image + " done\n------------------------------------")


def on_created(event):
    image = event.src_path
    if not os.path.exists(image):
        print("file dont exist")
    else: print("file exist")
    if image.split(".")[1] != 'csv':
        BarcodeReader(image)


if __name__ == "__main__":
    path = "img"  # set path
    patterns = ["*"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
