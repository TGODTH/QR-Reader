"""
*Important libraries*
#pip install pdf2image
#pip install opencv-python
#pip install pyzbar
#pip install watchdog
#pip install python-poppler
#pip install numpy
"""
import cv2
from pyzbar.pyzbar import decode
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import csv
from pdf2image import convert_from_path
import os


def Readbarcode(image, oldname):
    print("-----------------------------------------------------------------\nreading " + oldname)
    img = cv2.imread(image)
    detectedbarcodes = decode(img)

    if not detectedbarcodes:
        return "NotDetected_"
    else:
        qr_count = 0
        image_path = oldname.split(".")
        image_name = oldname.lstrip(path + '\\')
        for barcode in detectedbarcodes:
            qr_count += 1
            (x, y, w, h) = barcode.rect
            if barcode.data != "":
                print(f"QR:{qr_count} data - " + str(barcode.data))
                print(f"QR:{qr_count} type - " + str(barcode.type))

                csvheader = ['FileName', 'decodeStatus', 'row', 'BCLocation', 'BCType', 'BCTEXT']
                csvdata = ["Done_" + image_name, 1, qr_count, f'{x};{y}', barcode.type, barcode.data]
                with open(f'{image_path[0]}.csv', 'a', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    # write the header
                    if qr_count == 1:
                        writer.writerow(csvheader)
                    # write the data
                    writer.writerow(csvdata)
            else:
                return "QRempty_"
        return "Done_"


def on_created(event):
    global num
    num += 1
    exception = ["Reading", "ReadError", "NotDetected", "Done"]
    if (exception[0] not in event.src_path) and (exception[1] not in event.src_path) and (
            exception[2] not in event.src_path) and (exception[3] not in event.src_path) and (
            event.src_path[-3:] != "csv"):
        oldname = event.src_path
        # newname = "temp\\" + "Reading_" + oldname.lstrip(path + '\\')
        newname = f"temp\\Reading{num}." + oldname.split(".")[-1]
        if oldname[-3:] == "pdf":
            newpng = (newname.rstrip(".pdf"))
            page = convert_from_path(oldname, 500, poppler_path=r"Libs\poppler\Library\bin")
            page[0].save(newpng + '.jpg', 'JPEG')
            os.rename(oldname, newname)
            os.rename(newname, path + '\\' + Readbarcode(newpng + ".jpg", oldname) + oldname.lstrip(path + '\\'))
            os.remove(newpng + ".jpg")
        else:
            os.rename(oldname, newname)
            os.rename(newname, path + '\\' + Readbarcode(newname, oldname) + oldname.lstrip(path + '\\'))

num = 0
if __name__ == "__main__":
    path = "img"  # set path

    # eventsrc_path = path+"\\123.png"
    # exception = ["Reading", "ReadError", "NotDetected", "Done"]
    # if (exception[0] not in eventsrc_path) and (exception[1] not in eventsrc_path) and (
    #         exception[2] not in eventsrc_path) and (exception[3] not in eventsrc_path):
    #     oldname = eventsrc_path
    #     newname = "temp\\" + "Reading_" + oldname.lstrip(path + '\\')
    #     if oldname[-3:] == "pdf":
    #         newpng = (newname.rstrip(".pdf"))
    #         page = convert_from_path(oldname, 500, poppler_path=r"Libs\poppler\Library\bin")
    #         page[0].save(newpng + '.jpg', 'JPEG')
    #         os.rename(oldname, newname)
    #         os.rename(newname, path + Readbarcode(newpng, oldname) + oldname.lstrip(path + '\\'))
    #         os.remove(newpng)
    #     else:
    #         os.rename(oldname, newname)
    #         os.rename(newname, path + '\\' + Readbarcode(newname, oldname) + oldname.lstrip(path + '\\'))



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
