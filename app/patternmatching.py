from numbers import Number
import cv2
import os
import numpy as np

# Load the Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the Local Binary Patterns (LBP) face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

from skimage.feature import local_binary_pattern


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


# Function to extract the features of a face
def extract_face_features(face):
    # Convert the face to grayscale
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

    # Resize the face to 100x100 pixels
    face_resized = cv2.resize(gray, (100, 100))

    # Extract Local Binary Patterns (LBP) from the face
    face_lbp = local_binary_pattern(face_resized, 8, 1)

    # Return the LBP features as a 1D array
    return face_lbp.flatten()


# Function to find the closest match to a face among a list of faces
def find_closest_match(face, face_images):
    # Extract the features of the face to match
    face_features = extract_face_features(face)

    # Initialize the minimum distance and closest match
    min_distance = float('inf')
    closest_match = None
    match_index = 0

    # Loop through each face and find the distance to the face to match
    for i, other_face in enumerate(face_images):
        # Extract the features of the other face
        other_features = extract_face_features(other_face)

        # Compute the distance between the two faces using L2 norm
        distance = np.linalg.norm(face_features - other_features)

        # Update the minimum distance and closest match if necessary
        if distance < min_distance:
            min_distance = distance
            closest_match = other_face
            match_index = i

    return closest_match, match_index


# Function to extract all faces from an image and blur them except the closest match
def extract_faces_from_image(image_path, my_face, anonymization_style):
    img = cv2.imread(image_path)
    image = image_resize(img, height=800)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(30, 30)
    )

    print("[INFO] Found {0} Faces!".format(len(faces)))

    face_images = []
    for i, (x, y, w, h) in enumerate(faces):
        face_image = image[y:y + h, x:x + w]
        face_images.append(face_image)

    closest_match, match_index = find_closest_match(my_face, face_images)

    for i, (x, y, w, h) in enumerate(faces):
        if i != match_index:
            face_roi = image[y:y + h, x:x + w]

            # Anonymize based on selected style
            if anonymization_style == 'blurring':
                anonymized_roi = cv2.GaussianBlur(face_roi, (23, 23), 30)
            elif anonymization_style == 'black box':
                anonymized_roi = np.zeros_like(face_roi)
            elif anonymization_style == 'pixelate':
                anonymized_roi = cv2.resize(cv2.resize(face_roi, (16, 16)), (w, h), interpolation=cv2.INTER_NEAREST)
            else:
                anonymized_roi = face_roi  # Or any default anonymization

            image[y:y + h, x:x + w] = anonymized_roi  # replacing the face roi with anonymized one

    # Save the anonymized image
    cv2.imwrite('anonymized_image.jpg', image)
    print("[INFO] Image anonymized_image.jpg written to filesystem: ", os.path.exists('anonymized_image.jpg'))

    return faces, face_images, closest_match


# Function to find the closest match to your face in an image
def find_closest_match_for_image(image_path, ans):
    # Load your face image
    my_face_img = cv2.imread('anchor2.jpg')
    my_face = image_resize(my_face_img, height=800)

    # Extract all faces from the image and blur them except the closest match
    faces, face_images, closest_match = extract_faces_from_image(image_path, my_face,ans)

    return closest_match


'''# Find the closest match to your face in a group photo
image_path = 'friends.jpg'
closest_match = find_closest_match_for_image(image_path)

# Save the closest match to your face
cv2.imwrite('closest_match.jpg', closest_match)'''