import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
train_data_ads = pd.read_csv('/content/drive/MyDrive/decrypted_file/train/train_data_ads.csv')
train_data_feeds = pd.read_csv('/content/drive/MyDrive/decrypted_file/train/train_data_feeds.csv')
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
def preprocess_data(df):
    label_encoders = {}
    scalers = {}

    categorical_columns = df.select_dtypes(include=['object']).columns
    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le



    numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns
    for col in numerical_columns:
        scaler = MinMaxScaler()
        df[col] = scaler.fit_transform(df[col].values.reshape(-1, 1))
        scalers[col] = scaler

    return df, label_encoders, scalers

train_ads, train_ads_label_encoders, train_ads_scalers = preprocess_data(train_data_ads)
train_feeds, train_feeds_label_encoders, train_feeds_scalers = preprocess_data(train_data_feeds)

import tensorflow as tf
from tensorflow.keras.layers import Dense, LeakyReLU, BatchNormalization, Reshape, Flatten
from tensorflow.keras.models import Sequential

def build_generator(input_dim, output_dim):
    model = Sequential()
    model.add(Dense(128, input_dim=input_dim))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(256))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(output_dim))
    return model

def build_discriminator(input_dim):
    model = Sequential()
    model.add(Dense(512, input_dim=input_dim))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(256))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(128))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(1, activation='sigmoid'))
    return model

def compile_gan(generator, discriminator):
    discriminator.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    discriminator.trainable = False
    gan_input = tf.keras.Input(shape=(generator.input_shape[1],))
    generated_data = generator(gan_input)
    gan_output = discriminator(generated_data)
    gan = tf.keras.Model(gan_input, gan_output)
    gan.compile(loss='binary_crossentropy', optimizer='adam')
    return gan

def drop_columns_if_exist(df, columns):
    existing_columns = [col for col in columns if col in df.columns]
    return df.drop(columns=existing_columns)

def train_gan(generator, discriminator, gan, data, epochs=10000, batch_size=64, print_interval=1000):
    half_batch = batch_size // 2

    for epoch in range(epochs):
        idx = np.random.randint(0, data.shape[0], half_batch)
        real_data = data[idx]
        real_labels = np.ones((half_batch, 1))

        noise = np.random.normal(0, 1, (half_batch, generator.input_shape[1]))
        fake_data = generator.predict(noise)
        fake_labels = np.zeros((half_batch, 1))

        d_loss_real = discriminator.train_on_batch(real_data, real_labels)
        d_loss_fake = discriminator.train_on_batch(fake_data, fake_labels)
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

        noise = np.random.normal(0, 1, (batch_size, generator.input_shape[1]))
        valid_y = np.ones((batch_size, 1))
        g_loss = gan.train_on_batch(noise, valid_y)

        if epoch % print_interval == 0:
            print(f"{epoch} [D loss: {d_loss[0]}] [G loss: {g_loss}]")

def generate_synthetic_data(generator, num_samples, scalers, columns):
    noise = np.random.normal(0, 1, (num_samples, generator.input_shape[1]))
    synthetic_data = generator.predict(noise)

    for i, col in enumerate(columns):
        scaler = scalers[col]
        synthetic_data[:, i] = scaler.inverse_transform(synthetic_data[:, i].reshape(-1, 1)).flatten()
    
    return synthetic_data

data_ads = drop_columns_if_exist(train_ads, ['log_id', 'user_id'])
data_feeds = drop_columns_if_exist(train_feeds, ['log_id', 'user_id'])

scalers = {}
for col in data_ads.columns:
    scaler = MinMaxScaler()
    data_ads[col] = scaler.fit_transform(data_ads[col].values.reshape(-1, 1))
    scalers[col] = scaler

data_ads_values = data_ads.values


generator_ads = build_generator(input_dim=100, output_dim=data_ads_values.shape[1])
discriminator_ads = build_discriminator(input_dim=data_ads_values.shape[1])
gan_ads = compile_gan(generator_ads, discriminator_ads)

train_gan(generator_ads, discriminator_ads, gan_ads, data_ads_values)
synthetic_data_ads = generate_synthetic_data(generator_ads, 1000, scalers, data_ads.columns)
synthetic_data_ads_dataframe = pd.DataFrame(synthetic_data_ads, columns=data_ads.columns)
synthetic_data_ads_dataframe.to_csv('synthetic_train_ads.csv', index=False)


scalers2 = {}
for col in data_feeds.columns:
    scaler = MinMaxScaler()
    data_ads[col] = scaler.fit_transform(data feeds[col].values.reshape(-1, 1))
    scalers2[col] = scaler

data_feeds_values = data_feeds.values


generator_feeds = build_generator(input_dim=100, output_dim=data_feeds_values.shape[1])
discriminator_feeds = build_discriminator(input_dim=data_feeds_values.shape[1])
gan_feeds = compile_gan(generator_feeds, discriminator_feeds)

train_gan(generator_feeds, discriminator_feeds, gan_feeds, data_feeds_values)
synthetic_data_feeds = generate_synthetic_data(generator_feeds, 1000, scalers2, data_feeds.columns)
synthetic_data_feeds_dataframe = pd.DataFrame(synthetic_data_feeds, columns=data_feeds.columns)
synthetic_data_feeds_dataframe.to_csv('synthetic_train_feeds.csv', index=False)