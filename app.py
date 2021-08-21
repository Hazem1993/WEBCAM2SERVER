#first we import the libraries we need for face recognition
from flask import Flask, render_template, Response
import cv2
from datetime import datetime
import face_recognition
import numpy as np
app =Flask(__name__)

#To operate video steaming from webcam
camera = cv2.VideoCapture(0)

# Load samples of  pictures and learn how to recognize it which are then used as reference

AmrDiab_image = face_recognition.load_image_file("Amr Diab/Amr-Diab.jpg")
bradley_image = face_recognition.load_image_file("Bradley/bradley.jpg")
BillGates_image = face_recognition.load_image_file("Bill Gates/Bill gates.jpg")
ElonMusk_image = face_recognition.load_image_file("Elon Musk/Elon Musk.jpg")
MarkZuckerberg_image = face_recognition.load_image_file("Mark zuckerberg/Mark zuckerberg.jpg")

# Encode the Loaded samples of images
bradley_face_encoding = face_recognition.face_encodings(bradley_image)[0]
AmrDiab_face_encoding = face_recognition.face_encodings(AmrDiab_image)[0]
ElonMusk_face_encoding = face_recognition.face_encodings(ElonMusk_image)[0]
MarkZuckerberg_face_encoding = face_recognition.face_encodings(MarkZuckerberg_image)[0]
BillGates_face_encoding = face_recognition.face_encodings(BillGates_image)[0]


# Create arrays of known face encodings and their names
known_face_encodings = [
    MarkZuckerberg_face_encoding,
    ElonMusk_face_encoding,
    AmrDiab_face_encoding,
    BillGates_face_encoding,
    bradley_face_encoding
]

# Create arrays of names for face encodings
known_face_names = [
    "Mark Zuckerberg",
    "Elon Musk",
    "Amr Diab",
    "Bill Gates",
    "Bradly"
]
# Initialize some variables
img_item = []
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

#create a function to detect time of captured faces if they are found in trained models


def MarkAttendacne(name,y, rgb_small_frame):
    with open('Attend_Date.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dt_string = now.strftime("%H:%M:%S")
            f.writelines(f'\n{name},{dt_string}')
            img_item = f"filename_{y:04}.png"
            cv2.imwrite(img_item,  rgb_small_frame)

#While loop to continuously capture Video streaming through webcam


def gen_frames():
    x = 0
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    MarkAttendacne(name, x, rgb_small_frame)
                    x = x + 1
                face_names.append(name)


            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 1)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

             #following lines are used to stream video on website
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__=='__main__':
    app.run(debug=True)
