import cv2
import pytesseract


def run(path):
    image=cv2.imread(path)
    box = pytesseract.image_to_data(image)
    print(box)
    for line in box.split("\n"):
        if "left" in line:
            continue

        args = line.split("\t")
        if int(args[3]) != 0:
            continue
        if int(args[2]) == 0:
            continue

        box1 = (int(args[6]), int(args[7]), int(args[6]) + int(args[8]), int(args[7]) + int(args[9]))
        cv2.rectangle(image,(int(args[6]), int(args[7])),(int(args[6]) + int(args[8]), int(args[7]) + int(args[9])),(255, 0, 0), 2)
    cv2.imwrite(r"C:\temp\box\a.jpg",image)

if __name__ == '__main__':
    # run(r"C:\temp\image\b9c0cc34a83911e9a01a00ac37466cf9.jpg")
    a=pytesseract.image_to_string(r"C:\temp\tp\QQ截图20200117144254.png","eng")
    print(a)