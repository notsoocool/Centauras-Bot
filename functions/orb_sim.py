import cv2
from PIL import Image as im
from skimage.metrics import structural_similarity
import os
import numpy as np

# FHD resolution
frameWidth = 1920
frameHeight = 1080

# HD resolution
# frameWidth = 1280
# # frameHeight = 720

# # 480p resolution
# frameWidth = 852
# frameHeight = 480


# Returns only the video name i.e if Video Path is 'Resources/video1.png' then it will return video1 as string
def only_video_name(video_path):
    _, file_name = os.path.split(video_path)
    file_name_without_ext = os.path.splitext(file_name)[0]
    return file_name_without_ext


# Gives the actual length of video in seconds
def length_of_video(video_path):
    cap = cv2.VideoCapture(video_path)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    return length


# Gives the percentage of text in any Image, to compare two similar images with same text and to find which has more
def getPercentage(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 3)

    mask = thresh.copy()
    mask = cv2.merge([mask, mask, mask])

    picture_threshold = image.shape[0] * image.shape[1] * .05
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        area = cv2.contourArea(c)
        # if area < picture_threshold:
        cv2.drawContours(mask, [c], -1, (0, 0, 0), -1)

    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    result = cv2.bitwise_xor(thresh, mask)

    # cv2.imshow('thresh', thresh)
    cv2.imshow('result', result)
    # cv2.imshow('mask', mask)

    text_pixels = cv2.countNonZero(result)
    percentage = (text_pixels / (image.shape[0] * image.shape[1])) * 100 * 100
    # print('Percentage: {:.2f}%'.format(percentage))
    return percentage


# Works well with images of different dimensions, gives the Percentage of similarity between 2 images
# 1 means exact similar and 0 means completely different
def orb_sim(img1, img2):
    # SIFT is no longer available in cv2 so using ORB
    orb = cv2.ORB_create()

    # detect keypoints and descriptors
    kp_a, desc_a = orb.detectAndCompute(img1, None)
    kp_b, desc_b = orb.detectAndCompute(img2, None)

    # define the bruteforce matcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # perform matches.
    matches = bf.match(desc_a, desc_b)
    # Look for similar regions with distance < 50. Goes from 0 to 100 so pick a number between.
    similar_regions = [i for i in matches if i.distance < 30]
    if len(matches) == 0:
        return 0
    return len(similar_regions) / len(matches)


# To get the list of all different frames in a continuous video, I mean every change of screen is recorded here
def get_list_of_frames():
    video_name = 'Recorded'
    video_name = video_name + ".avi"
    video_path = os.path.join("E:/WEB_DEVELOPMENT/selenium/centauras_bot/", video_name)

    # If data folder is not available then create it to store your smart Images
    try:
        if not os.path.exists('./images/data/'):
            os.makedirs('./images/data/')
    except OSError:
        print ('Error: Creating directory of data')

    save_path = "./images/data/"
    no_of_frames = length_of_video(video_path)
    # 1 second has 30 frames
    print("Total no. frames is : " + str(no_of_frames))  # 4278 frames => 142 seconds => 2.37 minutes

    cap = cv2.VideoCapture(video_path)
    fimages = []
    ct = 0
    simg = np.zeros([512, 512, 3], dtype=np.uint8)
    simg.fill(255)
    img1 = cv2.resize(simg, (frameWidth, frameHeight))
    img2 = None
    orb_similarity = None
    while True:
        success, img = cap.read()
        ct += 1
        if not success:
            break
        img = cv2.resize(img, (frameWidth, frameHeight))
        cv2.imshow("Result", img)
        img2 = img
        if ct%24 == 0:  # Skipping the frames
            orb_similarity = orb_sim(img1, img2)  # 1.0 means identical. Lower = not similar
            print(str(ct) + " - " + str(orb_similarity))
            if orb_similarity < 0.8:
                fimages.append([img1, orb_similarity, ct])
            img1 = img2
        if cv2.waitKey(1) and 0xFF == ord('q'):
            break
    fimages.append([img2, orb_similarity, no_of_frames])
    return fimages


# As we get all useful frames, now out of all screen change's frame, get the smartest frame i.e with max text
def refine_images():
    images = get_list_of_frames()
    print("length of final frames is : " + str(len(images)))
    visited = set()
    fimages = []
    for i in range(len(images)):
        if i not in visited:
            visited.add(i)
            id = i
            mx_val = getPercentage(images[i][0])
            for j in range(len(images)):
                if j not in visited:
                    img1 = images[i][0]
                    img2 = images[j][0]
                    orb_similarity = orb_sim(img1, img2)
                    if orb_similarity > 0.8:
                        visited.add(j)
                        val = getPercentage(images[j][0])
                        if val > mx_val:
                            mx_val = val
                            id = j
            fimages.append(images[id])
    return fimages


# Just printing the final smart frames along with their frame number and orb_similarity
def print_save_final_images():
    end_time = []
    fimages = refine_images()
    for img in fimages:
        data = im.fromarray(img[0])
        print(str(img[2]) + " - " + str(img[1]))
        data.show()

    for img in fimages[1:]:
        data = im.fromarray(img[0])
        filename = "img" + str(img[2]) + ".png"
        end_time.append(img[2]//24)
        npath = os.path.join("./images/data/", filename)
        data.save(npath)

    end_time.sort()
    for time in end_time:
        print(time, end=" , ")

    return end_time


# end_time_list = print_save_final_images()

cv2.waitKey(0)