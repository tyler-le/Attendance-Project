import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

# import images automatically from BaseImagesOfStudents folder
path = 'BaseImagesOfStudents'
imagesOfStudents = []
namesOfStudents = []
hereNameList = []

listWithJPGExtension = os.listdir(path)

# go through BaseImagesOfStudents folder and grab names
for fileName in listWithJPGExtension:
    currImg = cv2.imread(f'{path}/{fileName}')
    imagesOfStudents.append(currImg)
    # remove .jpg from name
    namesOfStudents.append(os.path.splitext(fileName)[0])

print(namesOfStudents)


# find encodings for each image and put in encodeList
def findEncodings(images):
    listOfEncodings = []
    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encoding = face_recognition.face_encodings(image)[0]
        listOfEncodings.append(encoding)
    return listOfEncodings


def markAttendance(studentName):
    # open csv with rw permissions
    with open('Attendance.csv', 'r+') as f:
        myCSVList = f.readlines()

        # iterate through each line and split between commas
        for line in myCSVList:
            entry = line.split(',')
            # since it splits name and time, we want name list to only have first entry (name)
            hereNameList.append(entry[0])

        # check if current name is present or not
        # if not present, then add current time into list
        if studentName not in hereNameList:
            now = datetime.now()
            dateString = now.strftime('%b %d at %I:%M %p')
            f.writelines(f'\n{studentName},{dateString}')


encodeListKnown = findEncodings(imagesOfStudents)
print('Finished Encoding...')

# initialize webcam
#cap = cv2.VideoCapture(0) # for webcam

while True:
    #success, img = cap.read() # for webcam
    img = cv2.imread('ScreenshotOfZoomClassForAttendance/zoomCelebrity.jpg')  # for screenshot

    scaledImage = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    scaledImage = cv2.cvtColor(scaledImage, cv2.COLOR_BGR2RGB)

    # find face location and send each location to encoding
    facesAtCurrentFrame = face_recognition.face_locations(scaledImage)
    encodingsAtCurrentFrame = face_recognition.face_encodings(scaledImage, facesAtCurrentFrame)
    # iterate through all faces found in current frame
    # compare all these faces with all the encodings in encodeListKnown
    # grabs one faceLoc in facesCurrFrame and grab encoding from encodeCurrFrame
    for faceEncoding, faceLocation in zip(encodingsAtCurrentFrame, facesAtCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, faceEncoding)
        faceDis = face_recognition.face_distance(encodeListKnown, faceEncoding)

        # find index at lowest encoding value
        matchIndex = np.argmin(faceDis)

        # now we know who the person is.
        # display name and display rectangle
        if matches[matchIndex]:
            name = namesOfStudents[matchIndex]
            # print(name)

            y1, x2, y2, x1 = faceLocation
            # multiply by 4 since we scaled down image to 1/4 the size previously
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            markAttendance(name)

        imageResized = cv2.resize(img, (640, 360))
        cv2.imshow("Results", imageResized)
        cv2.waitKey(1)
