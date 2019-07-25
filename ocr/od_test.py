import numpy as np
import tensorflow as tf

from matplotlib import pyplot as plt
from PIL import Image

from object_detection.utils import label_map_util
# from object_detection.utils import visualization_utils as vis_util
from ocr import utils as vis_util


# What model to download.
# model_path="C:/data/taa/train_model/save_model"
pb_path="C:/data/taa/save/frozen_inference_graph.pb"
label_path="C:/data/taa/pascal_label_map.pbtxt"
test_image="C:/temp/png/page_0.jpg"






#Load a (frozen) Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(pb_path, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')
#Loading label map
label_map = label_map_util.load_labelmap(label_path)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=20, use_display_name=True)
category_index = label_map_util.create_category_index(categories)
#Helper code
def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


# For the sake of simplicity we will use only 2 images:
# image1.jpg
# image2.jpg

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)

with detection_graph.as_default():
  with tf.Session(graph=detection_graph) as sess:


    #for image_path in TEST_IMAGE_PATHS:
    image = Image.open(test_image)
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    # Each box represents a part of the image where a particular object was detected.
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')
    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8)


    # count = 0
    # for i in range(100):
    #     if scores is None or final_score[i] > 0.5:
    #         count = count + 1
    # print ('the count of objects is: ', count)

    plt.figure(figsize=IMAGE_SIZE)
    plt.imshow(image_np)
    plt.show()