from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Create an image data generator with augmentation parameters
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2  # Use 20% of the data as validation data
)

# Training data generator
train_generator = datagen.flow_from_directory(
    './images/falling wedge pattern/',
    target_size=(256, 256),
    batch_size=32,
    class_mode='binary',  # or 'categorical' if more than two classes
    subset='training'
)

# Validation data generator
validation_generator = datagen.flow_from_directory(
    './images/falling wedge pattern/',
    target_size=(256, 256),
    batch_size=32,
    class_mode='binary',  # or 'categorical' if more than two classes
    subset='validation'
)
