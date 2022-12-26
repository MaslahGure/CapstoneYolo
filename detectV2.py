import tensorflow as tf
import cv2
import numpy as np


def draw_bounding_box(image, xmin, ymin, xmax, ymax, label):
    """Draws a bounding box on the image and displays the label."""
    cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
    cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 2)


def preprocess_image(image):
    """Resizes and normalizes the image."""
    image = cv2.resize(image, (300, 300))
    image = image.astype(np.float32)
    image /= 255
    return np.expand_dims(image, 0)


# Load the TensorFlow Lite model.
interpreter = tf.lite.Interpreter(model_path="best.tflite")

# Allocate memory for the model.
interpreter.allocate_tensors()

# Get input and output tensors.
input_tensor = interpreter.tensor(interpreter.get_input_details()[0]["index"])
output_tensors = [interpreter.tensor(i["index"])
                  for i in interpreter.get_output_details()]

# Load the labelmap.
with open("labelmap.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]

# Set the confidence threshold.
confidence_threshold = 0.5

# Open the camera.
cap = cv2.VideoCapture(0)

while True:
    # Get a frame from the camera.
    ret, frame = cap.read()

    # Preprocess the frame.
    frame = preprocess_image(frame)

    # Run inference on the frame.
    input_tensor = interpreter.tensor(interpreter.get_input_details()[0]["index"])
    input_tensor[:, :, :] = frame
    interpreter.invoke()

    # Get the output.
    boxes = output_tensors[0]
    classes = output_tensors[1]
    scores = output_tensors[2]

    # Loop over the detections and draw bounding boxes.
    for i in range(boxes.shape[1]):
        if scores[0, i] > confidence_threshold:
            ymin, xmin, ymax, xmax = boxes[0, i]
            label = labels[int(classes[0, i])]
            draw_bounding_box(frame, xmin, ymin, xmax, ymax, label)

            # Perform different actions based on the label.
            if label == "tomato":
                print("Tomato detected!")
            elif label == "chilli":
                print("Chilli detected!")

    # Display the frame.
    frame = np.squeeze(frame, axis=0)

    cv2.imshow("Frame", frame)

    # Check if the user pressed 'q'.
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and destroy the window.
cap.release()
cv2.destroyAllWindows()
