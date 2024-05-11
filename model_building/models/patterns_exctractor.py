import cv2
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array, load_img

# Define the path to your image
image_path = './images/dabc20923094ec087782ea3cd7bb88c3.jpg'

# Load the image
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB

# Resize the image to the required size of 256x256 pixels
image = cv2.resize(image, (256, 256))

# Normalize the image
image = image.astype('float32') / 255.0

# Convert the image to an array suitable for a Keras model
image = img_to_array(image)
image = np.expand_dims(image, axis=0)  # Model expects images in the shape (1, 256, 256, 3)
print(f"Image: {image.shape}")


# Now 'image' is ready to be used as an input for your model
print("Preprocessing complete. Image is ready for model input.")
