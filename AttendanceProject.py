import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

# import images automatically from ImagesAttendance folder
path = 'ImagesAttendance'
images = []
classNames = []
myList = os.listdir(path)
print(myList)

# go through ImagesAttendance folder and grab names
for cl in myList:
    currImg = cv2.imread(f'{path}/{cl}')
    images.append(currImg)
    # remove .jpg from name
    classNames.append(os.path.splitext(cl)[0])
print(classNames)


# find encodings for each image and put in encodeList
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):
    # open csv with rw permissions
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []

        # iterate through each line and split between commas
        for line in myDataList:
            entry = line.split(',')
            # since it splits name and time, we want name list to only have first entry (name)
            nameList.append(entry[0])

        # check if current name is present or not
        # if not present, then add current time into list
        if name not in nameList:
            now = datetime.now()
            dateString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dateString}')


encodeListKnown = findEncodings(images)
print('Encoding Complete')

# initialize webcam
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # find face location and send each location to encoding
    facesCurrFrame = face_recognition.face_locations(imgS)
    encodeCurrFrame = face_recognition.face_encodings(imgS, facesCurrFrame)
    # iterate through all faces found in current frame
    # compare all these faces with all the encodings in encodeListKnown
    # grabs one faceLoc in facesCurrFrame and grab encoding from encodeCurrFrame
    for encodeFace, faceLoc in zip(encodeCurrFrame, facesCurrFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print(faceDis)
        # find index at lowest encoding value
        matchIndex = np.argmin(faceDis)

        # now we know who the person is.
        # display name and display rectangle
        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            # print(name)

            y1, x2, y2, x1 = faceLoc
            # multiply by 4 since we scaled down image to 1/4 the size in line 39
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            markAttendance(name)

        cv2.imshow('Webcam', img)
        cv2.waitKey(1)