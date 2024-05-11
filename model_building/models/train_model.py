import tensorflow as tf

batch_size = 32
img_height = 180
img_width = 180


def train_gen():
    # Training data generator
    train_generator = tf.keras.utils.image_dataset_from_directory(
        './images/patterns/',
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size
    )
    class_names = train_generator.class_names
    print(class_names)
    return train_generator


def train_val():
    # Validation data generator
    validation_generator = tf.keras.utils.image_dataset_from_directory(
        './images/patterns/',
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size

    )
    return validation_generator


def build_model():

    train_ds = train_gen()
    val_ds = train_val()

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    num_classes = 2
    model = tf.keras.Sequential([
        tf.keras.layers.Rescaling(1. / 255),
        tf.keras.layers.Conv2D(32, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(32, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(32, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(num_classes)
    ])

    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy'])

    return model


def fit_model():
    model = build_model()
    train_ds = train_gen()
    val_ds = train_val()
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=10
    )
    model.save('./model/patterns.h5')  # Save the model as an HDF5 file


if __name__ == '__main__':
    fit_model()
