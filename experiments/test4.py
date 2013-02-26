
import cv2
import numpy as np
import PIL
import matplotlib.pyplot as plt

filename = "../tests/1.mp4"

IMAGE_DEVIATION_TRESHOLD = 10.0

def get_frame_set(file_name, dt, max_frame_count = 10, skip_frames = 20):
    i = 0
    frames = []
    source = cv2.VideoCapture(file_name)
    _,frame = source.read()

    while(True):
        if i > skip_frames:
            break
        source.read()
        i+=1

    while(True):
        if len(frames) >= max_frame_count:
            break
        _,frame = source.read()
        if (frame == None):
            break
        if i % dt == 0:
            treshold = get_picture_std(frame)
            if treshold > IMAGE_DEVIATION_TRESHOLD:
                print treshold
            frames.append(np.copy(frame))
        i+=1
    return frames

def get_picture_std(img):
    return np.asarray(img).std(axis=1).std()

def process(frame_set):
    sample_images = np.concatenate([image.reshape(1,image.shape[0], image.shape[1]) 
                                for image in frame_set], axis=0)

    # determine per-pixel variablility, std() over all images
    variability = np.float32(sample_images.std(axis=0))
    #(thresh, variability) = cv2.threshold(variability, 20, 255, cv2.THRESH_BINARY)

    # show image of these variabilities
    plt.figure(2)
    plt.imshow(variability, cmap=plt.cm.gray, interpolation="nearest", origin="lower")

    # determine bounding box
    thresholds = [5,10,12]
    colors = ["r", "g", "b"]
    for threshold, color in zip(thresholds, colors): #variability.mean()
        non_empty_columns = np.where(variability.min(axis=0)<threshold)[0]
        non_empty_rows = np.where(variability.min(axis=1)<threshold)[0]
        try:
            boundingBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))
        except ValueError:
            print "is too small"
            continue
        # plot and print boundingBox
        bb = boundingBox
        plt.plot([bb[2], bb[3], bb[3], bb[2], bb[2]],
                 [bb[0], bb[0],bb[1], bb[1], bb[0]])
        #print boundingBox
    plt.xlim(0,variability.shape[1])
    plt.ylim(variability.shape[0],0)
    plt.legend()

    plt.show()

def process2(frame_set):
    new_frames = []

    avg = np.float32(cv2.cvtColor(frame_set[0], cv2.COLOR_BGR2GRAY))
    for frame in frame_set:
        cv2.accumulateWeighted(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),avg,0.01)
        res = cv2.convertScaleAbs(avg)
        (thresh, res) = cv2.threshold(res, 205, 255, cv2.THRESH_BINARY)

        new_frames.append(np.copy(res))

    return new_frames, res

if __name__ == '__main__':
    frames = get_frame_set(filename, 15, 40, 100)
    frames, res = process2(frames)
    cv2.namedWindow("frame")
    cv2.imshow("frame", res)
    cv2.waitKey(10000)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(20,20))
    mat = cv2.dilate(res,kernel)

    cv2.imshow("frame",mat)
    cv2.waitKey(10000)

    contours, hierarchy = cv2.findContours(mat,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    res = cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(res, contours,-1,(0,255,0),3)

    cv2.imshow("frame", res)
    cv2.waitKey(10000)

    #loop = True
    #while(loop):
    #    for frame in frames:
    #        cv2.imshow("frame", frame)
    #        char = cv2.waitKey(100)
    #        if (char == 27):
    #            loop = False
    cv2.destroyAllWindows()
