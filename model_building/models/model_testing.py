import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

model_path = './model/patterns.h5'
model = tf.keras.models.load_model(model_path)


def load_and_preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(180, 180))  # Resize the image to match the model's expected input
    img_array = image.img_to_array(img)  # Convert the image to an array
    img_array = tf.expand_dims(img_array, 0)  # Create a batch
    img_array /= 255.0  # Normalize to [0,1] range as done during training
    return img_array


def predict_image(model, img_array):
    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])  # Applying softmax to convert logits to probabilities
    print(score)

    class_names = ['falling wedge pattern', 'rising wedge pattern']  # Adjust class names based on your training labels
    predicted_class = class_names[np.argmax(score)]
    confidence = np.max(score)

    return predicted_class, confidence


if __name__ == '__main__':
    # Load and preprocess the image
    test_image_path = './images/testing/origin.png'
    test_img_array = load_and_preprocess_image(test_image_path)

    # Predict the image class
    predicted_class, confidence = predict_image(model, test_img_array)
    print(f"Predicted class: {predicted_class}, Confidence: {confidence:.2f}")
