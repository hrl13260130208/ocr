

from pdf2image import convert_from_path
import tempfile
import PIL.Image as Image
import pytesseract
import cv2
import object_detection.export_inference_graph
from stanfordcorenlp import StanfordCoreNLP
import re

ocr_paths=[]

def main(filename, outputDir):
    print('filename=', filename)
    print('outputDir=', outputDir)
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(filename)
        for index, img in enumerate(images):
            if index >2:
                break
            image_path='%s/page_%s.png' % (outputDir, index)

            ocr_paths.append(image_path)
            img.save(image_path)

def get_abs(text):
    abs_num=text.lower().find("abstract")
    if abs_num!=-1:
        keywords_num=text.lower().find("keywords")
        if keywords_num!=-1:
            if keywords_num<abs_num+8:
                for section in get_sections(text):
                    if section.__len__() > 500:
                        num = section.rfind(".")
                        if num > 500:
                            return abs_clear(section[:num + 1])
            else:
                return abs_clear(text[abs_num+8:keywords_num])
        else:
            # print(text)
            abs=""
            for section in get_sections(text[abs_num+8:]):
                if section.__len__()>500:
                    abs=section
                    break
                else:
                    abs+=section+"\n"
                    if abs.__len__()>500:
                        break
            return abs_clear(abs)
    else:
        for section in get_sections(text):
            if section.__len__()>500:
                num=section.rfind(".")
                if num >500:
                    return abs_clear(section[:num+1])

def get_sections(text):
    return text.split("\n\n")

def abs_clear(abs):
    print("clear---------------",abs)
    abs=abs.strip()
    if abs[0] == ":":
        abs = abs[1:]
    print("last char:",abs[-1])
    if abs[-1] !="." and abs[-1] !="。":
        abs=abs+"."
    return abs

def create_box(pdf_path):
    path="C:/temp/box/"
    images = convert_from_path(pdf_path)
    for index, img in enumerate(images):
        image_path=path+"r"+str(index)+".png"
        img.save(image_path)
        image = cv2.imread(image_path)
        box = pytesseract.image_to_data(image)
        for line in box.split("\n"):
            # print(line)
            if "left" in line:
                continue
            args = line.split("\t")
            if int(args[3]) != 0:
                continue

            cv2.rectangle(image, (int(args[6]), int(args[7])),
                          (int(args[6]) + int(args[8]), int(args[7]) + int(args[9])), (255, 0, 0))
        cv2.imwrite(image_path, image)



def find_boxs(boxs,image_path):
    # print(pytesseract.image_to_data("C:/temp/png/page_0.jpg"))
    image_path="D:/data/temp/page_0.jpg"
    path="D:/data/temp"
    image = cv2.imread(image_path)
    box = pytesseract.image_to_data(image)
    for index,line in enumerate(box.split("\n")):
        # print(line)
        if "left" in line:
            continue
        args = line.split("\t")
        if int(args[3]) != 0:
            continue
        if int(args[2])==0:
            continue
        print("++++++++++++++++++++++",index)
        print("======================",args)
        A=(int(args[6]),int(args[7]))

        B=(int(args[6]) + int(args[8]), int(args[7]) + int(args[9]))
        print(int(args[6]),int(args[7]),int(args[6]) + int(args[8]),int(args[7]) + int(args[9]))
        new_image=image[int(args[7]):int(args[7]) + int(args[9]),int(args[6]):int(args[6]) + int(args[8])]
        # print(pytesseract.image_to_string(new_image))
        cv2.imwrite(path+str(index)+".jpg",new_image)
        # cv2.rectangle(image, (int(args[6]), int(args[7])),
        #               (int(args[6]) + int(args[8]), int(args[7]) + int(args[9])), (255, 0, 0))








def test():
    image_path = "C:/temp/png/page_0.jpg"
    image = cv2.imread(image_path)
    new_image = image[200:300, 400:1000]
    print(pytesseract.image_to_string(new_image))
    cv2.imwrite( "C:/temp/png/1.jpg", new_image)



def nlp():
    nlp = StanfordCoreNLP(r'C:\File\stanford-corenlp-full-2016-10-31')

    sentence = "Carlos Navarro-Retamal andJulio Caballero *"
    print('Tokenize:', nlp.word_tokenize(sentence))
    print('Part of Speech:', nlp.pos_tag(sentence))
    print( 'Named Entities:', nlp.ner(sentence))
    print('Constituency Parsing:', nlp.parse(sentence))

    print('Dependency Parsing:', nlp.dependency_parse(sentence))




if __name__ == "__main__":
    # create_box("C:/pdfs/dynamic/1a2dd1fa5d0511e9a9ca00ac37466cf9.pdf")
    # find_boxs(None,None)
    # nlp()
    # test()
    # # print("a".isalpha())
    # main('C:/temp/新建文件夹/0kKzRNRpJayT.pdf', 'C:/temp')
    # for path in ocr_paths:
    #     print("===========",path)
    #     print(pytesseract.image_to_string(path,lang="jpn"))
    #     print("+++++++++",get_abs(pytesseract.image_to_string(path,lang="jpn")))
    # print(pytesseract.image_to_string("C:/temp/12.png",lang="jpn"))
    # box=pytesseract.image_to_data("C:/temp/page_0.png")
    # image=cv2.imread("C:/temp/page_0.png")
    #
    # print(type(box))
    # block_dict={}
    # for line in box.split("\n"):
    #     # print(line)
    #     if "left" in line:
    #         continue
    #     args=line.split("\t")
    #     if int(args[3])!=0:
    #         continue
    #
    #     # block_num=args[2]
    #     # num1=int(args[6])
    #     # num2=int(args[6])+int(args[8])
    #     # num3=int(args[7]
    #     # num4=args[2]
    #     cv2.rectangle(image,(int(args[6]),int(args[7])),(int(args[6])+int(args[8]),int(args[7])+int(args[9])),(255, 0, 0))
    #     # print(args.__len__())
    #
    # # cv2.imshow("Text Detection", image)
    # #
    # # cv2.waitKey(0)
    # cv2.imwrite("C:/temp/r1.png",image)

    line="M . K o ua k ou  D je , S . D a b on n e, S. Ta g ro G u eh i a n d L . P a tr ic e K o u am e"
    pattern = "[A-Z]"
    new_string = re.sub(pattern, lambda x: " " + x.group(0),line.replace(" a n d "," A n d ").replace(" ",""))
    print(new_string)
