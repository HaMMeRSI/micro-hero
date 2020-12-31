import face_recognition


class BatmanRecognizer:

    def __init__(self, batman_path):
        batman_image = face_recognition.load_image_file(batman_path)
        self._batman = face_recognition.face_encodings(batman_image)[0]

    def is_batman(self, image, face_location):
        assert isinstance(face_location, tuple) & \
               len(face_location) == 4 & \
               all(isinstance(x, int) for x in face_location), 'face_location is not in the right format'

        img = face_recognition.load_image_file(image)
        encoding = face_recognition.face_encodings(img, [face_location])[0]
        return face_recognition.compare_faces([self._batman], encoding)[0]
