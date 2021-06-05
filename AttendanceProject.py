import csv

import cv2
import numpy as np
import face_recognition
import os
from datetime import date
import json
import pandas as pd

# import students automatically from 'uploads/students' folder
path = 'static/uploads'
imagesOfStudents = []
students_present = []
students_absent = []
json_dicts = []
date = date.today().strftime("%m/%d/%Y")


def folderHasImages():
    # Need to delete .DS_Store that randomly appears in the folder and causes bugs
    try:
        os.remove(f'{path}/students/.DS_Store')
    except:
        pass

    if len(os.listdir(f'{path}/students')) == 0:
        return False
    else:
        return True


def getStudentNames():
    studentNamesWithJPGExtension = os.listdir(f'{path}/students')
    names_of_students = []

    # go through BaseImagesOfStudents folder and grab names
    for fileName in studentNamesWithJPGExtension:
        # Check for hidden files starting with '.'
        if not fileName.startswith('.'):
            currImg = cv2.imread(f'{path}/students/{fileName}')
            imagesOfStudents.append(currImg)
            # remove .jpg from name
            names_of_students.append(os.path.splitext(fileName)[0])

    return names_of_students


# find encodings for each image and put in encodeList
def findEncodings(images):
    listOfEncodings = []
    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encoding = face_recognition.face_encodings(image)[0]
        listOfEncodings.append(encoding)
    return listOfEncodings


def markAttendance(lst):
    # Takes list of dictionaries and writes to JSON file.
    with open('static/data/data.json', 'w+') as file:
        str = json.dumps(lst)
        file.write(str)

    # Takes that JSON file and converts to CSV file.
    df = pd.read_json(r'static/data/data.json')
    df.to_csv(r'static/data/data.csv', index=None)


# CSV FILE IS BROKEN SINCE I REMOVED WHILE TRUE
def attendance():
    img = cv2.imread(f'{path}/class/class.jpg')
    if folderHasImages():
        names_of_students = getStudentNames()
        print(f'List of entire class: {names_of_students}')
        known_encodings = findEncodings(imagesOfStudents)
        print('Finished Encoding...')

        # find face location and send each location to encoding
        faces_at_current_frame = face_recognition.face_locations(img)
        encodings_at_current_frame = face_recognition.face_encodings(img, faces_at_current_frame)

        # iterate through all faces found in current frame
        # compare all these faces with all the encodings in known_encodings
        # grabs one faceLoc in facesCurrFrame and grab encoding from encodeCurrFrame
        for face_encoding, face_location in zip(encodings_at_current_frame, faces_at_current_frame):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            face_dist = face_recognition.face_distance(known_encodings, face_encoding)

            # find index at lowest encoding value
            match_index = np.argmin(face_dist)

            # now we know who the person is.
            # display name and display rectangle
            if matches[match_index]:
                name = names_of_students[match_index]

                top, right, bottom, left = face_location

                cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                students_present.append(name)

                # markAttendance(name)
    else:
        print('FOLDER IS EMPTY')

    students_absent = list(set(names_of_students) - set(students_present))

    # Is a list that holds dicts to be converted into JSON

    for student in students_present:
        entry = {
            'name': student,
            'present': True,
            'date': date
        }
        json_dicts.append(entry)

    for student in students_absent:
        entry = {
            'name': student,
            'present': False,
            'date': date
        }
        json_dicts.append(entry)

    markAttendance(json_dicts)
    cv2.imwrite(os.path.join(f'{path}/result', 'result.jpg'), img)