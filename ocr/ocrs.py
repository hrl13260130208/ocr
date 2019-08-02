import numpy as np
import tensorflow as tf

from PIL import Image
from object_detection.utils import label_map_util
import ocr.vis_utils as vis_util
import cv2
import pytesseract
from ocr.auto_annotation import xml_writer
import os


def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


class object_ocr():
    def __init__(self):
        pb_path = "C:/data/taa/save/frozen_inference_graph.pb"
        label_path = "C:/data/taa/pascal_label_map.pbtxt"
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(pb_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
        # Loading label map
        label_map = label_map_util.load_labelmap(label_path)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=20,
                                                                    use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

    def run(self,image_path):
        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as sess:
                # Definite input and output Tensors for detection_graph
                image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
                # Each box represents a part of the image where a particular object was detected.
                detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
                # for image_path in TEST_IMAGE_PATHS:
                image = Image.open(image_path)
                # the array based representation of the image will be used later in order to prepare the
                # result image with boxes and labels on it.
                image_np = load_image_into_numpy_array(image)
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
                # Each box represents a part of the image where a particular object was detected.
                boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
                # Actual detection.
                (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
                # Visualization of the results of a detection.
                return vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    self.category_index,
                    use_normalized_coordinates=True,
                    line_thickness=8)


class ocr():
    def __init__(self):
        self.object=object_ocr()
        self.image = None

    def get_items(self,image_path):
        item=self.object.run(image_path)
        self.image = cv2.imread(image_path)
        if item.keys().__len__()==0:
            return None

        box = pytesseract.image_to_data(self.image)

        new_item={}
        max_title_num=0
        max_author_num=0
        for index, line in enumerate(box.split("\n")):
            # print(line)
            if "left" in line:
                continue
            args = line.split("\t")
            if int(args[3]) != 0:
                continue
            if int(args[2]) == 0:
                continue

            box1 = (int(args[6]), int(args[7]), int(args[6]) + int(args[8]), int(args[7]) + int(args[9]))
            for key in item.keys():

                box2=(item[key][0],item[key][2],item[key][1],item[key][3])
                num=box_rectint(box1,box2)
                print(num)
                if num>0:
                    if "abs" in key:
                        if "abs" in new_item:
                            new_item["abs"].append(box1)
                        else:
                            new_item["abs"]=[box1]
                    elif "title" in key:
                        if "title" in new_item:
                            if num>max_title_num:
                                new_item["title"]=[box1]
                                max_title_num=num
                        else:
                            max_title_num=num
                            new_item["title"]=[box1]
                    elif "author" in key:
                        if "author" in new_item:
                            if num>max_author_num:
                                new_item["author"]=[box1]
                                max_author_num=num
                        else:
                            max_author_num=num
                            new_item["author"]=[box1]
        return new_item

    def read_items(self,items):
        print(items)
        string_dict = {}
        for key in items.keys():
            if items[key].__len__() > 1:
                if key == "abs":
                    for box in items[key]:
                        new_image = self.image[box[1]:box[3], box[0]:box[2]]
                        text = pytesseract.image_to_string(new_image)
                        if text.__len__()<100:
                            continue
                        string_dict[key] = text
                        break
            else:
                box = items[key][0]
                new_image = self.image[box[1]:box[3], box[0]:box[2]]
                string_dict[key] = pytesseract.image_to_string(new_image)

        return string_dict

    def read(self,image_path):
        dict=self.read_items(self.get_items(image_path))
        if "abs" in dict:
            if "\n\n" in dict["abs"]:
                lines=dict["abs"].split("\n\n")
                if lines[0].__len__()<15:
                    lines[0]=" "
                    dict["abs"]=" ".join(lines).strip()
            if ":" in dict["abs"]:
                num=dict["abs"].find(":")
                if num<15:
                    dict["abs"]= dict["abs"][num:].strip()


        return dict


    def auto_annotation(self,image_path):
        if image_path.rfind("/")!=-1:
            file_name = image_path[image_path.rfind("/")+1:]
            dir=image_path[:image_path.rfind("/")]
        else :
            file_name = image_path[image_path.rfind("\\")+1:]
            dir=image_path[:image_path.rfind("\\")]

        print(dir,file_name)

        items=self.get_items(image_path)
        if items==None:
            return
        print(items)
        shape=self.image.shape
        xml = xml_writer()
        xml.create_element(dir,file_name,shape[0],shape[1],shape[2])

        for key in items.keys():
            if items[key].__len__() > 1:
                if key == "abs":
                    for box in items[key]:
                        new_image = self.image[box[1]:box[3], box[0]:box[2]]
                        text = pytesseract.image_to_string(new_image)
                        if text.__len__() > 500:
                            xml.add_object("abs",box[0],box[1],box[2],box[3])
                            break
            else:
                box = items[key][0]
                print("++++++++++++++++",items[key][0])
                xml.add_object(key,box[0],box[1],box[2],box[3])

        xml.write()





def box_rectint(box1, box2):
    '''

    计算两个矩形框的重合度
    box=(xA,yA,xB,yB)
    xA,yA---矩形左上顶点的坐标
    xB,yB---矩形右下顶点的坐标
    :param box1:
    :param box2:
    :return:
    '''

    if mat_inter(box1, box2) == True:
        x01, y01, x02, y02 = box1
        x11, y11, x12, y12 = box2
        col = min(x02, x12) - max(x01, x11)
        row = min(y02, y12) - max(y01, y11)
        intersection = col * row
        area1 = (x02 - x01) * (y02 - y01)
        area2 = (x12 - x11) * (y12 - y11)
        coincide = intersection / (area1 + area2 - intersection)
        return coincide
    else:
        return 0

def mat_inter(box1, box2):
    # 判断两个矩形是否相交
    # box=(xA,yA,xB,yB)
    x01, y01, x02, y02 = box1
    x11, y11, x12, y12 = box2
    minx=max(x01,x11)
    miny=max(y01,y11)
    maxx=min(x02,x12)
    maxy=min(y02,y12)

    if minx> maxx or miny>maxy:
        return False
    else:
        return True





def test():
    pass



if __name__ == '__main__':
    print(ocr().read(r"C:\temp\image\b9c0cc34a83911e9a01a00ac37466cf9.jpg"))
    # ocr().auto_annotation("D:/data/image/00a33386a83b11e9bd8900ac37466cf9.jpg")


    # for file in os.listdir("D:/data/image"):
    #     if ".jpg" in file:
    #         path="D:/data/image/"+file
    #         # ocr().auto_annotation(path)
    #         ocr().read(path)






