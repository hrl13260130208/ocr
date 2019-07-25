from lxml import etree, objectify
import os
from PIL import Image
import cv2



class xml_writer:
    def __init__(self):
        self.anno_tree=None
        self.xml_path=None
    def create_element(self,dir,file_name,image_width,image_height,image_depth):
        E = objectify.ElementMaker(annotate=False)
        if dir.rfind("/")!=-1:
            folder_name=dir[dir.rfind("/"):]
        elif dir.rfind("\\")!=-1:
            folder_name = dir[dir.rfind("\\"):]
        else:
            folder_name="Unknown"

        self.xml_path=os.path.join(dir,file_name.replace(".jpg",".xml"))
        self.anno_tree = E.annotation(
            E.folder(folder_name),
            E.filename(file_name),
            E.path(os.path.join(dir,file_name)),
            E.source(
                E.database("Unknown")
            ),
            E.size(
                E.width(image_width),
                E.height(image_height),
                E.depth(image_depth)
            ),
            E.segmented(0),
        )
        self.anno_tree.set("verified", "no")

    def add_object(self,object_name,xmin,ymin,xmax,ymax):
        print("------------------")
        E = objectify.ElementMaker(annotate=False)
        temp=E.object(
                E.name(object_name),
                E.pose("Unspecified"),
                E.truncated(0),
                E.Difficult(0),
                E.bndbox(
                    E.xmin(xmin),
                    E.ymin(ymin),
                    E.xmax(xmax),
                    E.ymax(ymax)
                )
            )
        self.anno_tree.append(temp)

    def write(self):
        print("===========================",self.xml_path)
        if self.anno_tree==None:
            raise ValueError("请先创建xml!")
        etree.ElementTree(self.anno_tree).write(self.xml_path, pretty_print=True)



if __name__ == '__main__':
    image=cv2.imread("D:/data/taa/train_data_0709/bffc338c698e11e99dcd00ac37466cf9.jpg")
    # image=Image.open("D:/data/taa/train_data_0709/bffc338c698e11e99dcd00ac37466cf9.jpg")
    print(image.shape)
    # print(image.info)

    # E = objectify.ElementMaker(annotate=False)
    # anno_tree = E.annotation(
    #     E.folder('png'),
    #     E.filename("page_0"),
    #     E.path("C:/temp/png/page_0.jpg"),
    #     E.source(
    #         E.database("Unknown")
    #     ),
    #     E.size(
    #         E.width(1653),
    #         E.height(2339),
    #         E.depth(1)
    #     ),
    #     E.segmented(0),
    #     E.object(
    #         E.name("title"),
    #         E.pose("Unspecified"),
    #         E.truncated(0),
    #         E.Difficult(0),
    #         E.bndbox(
    #             E.xmin(100),
    #             E.ymin(200),
    #             E.xmax(300),
    #             E.ymax(400)
    #         )
    #     )
    #
    # )
    # anno_tree.set("verified","no")
    # etree.ElementTree(anno_tree).write("C:/temp/png/page_0.xml", pretty_print=True)
