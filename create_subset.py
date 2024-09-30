import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, LeakyReLU, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import RMSprop
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

# Load the dataset
data_path = r'C:\Users\sonav\Downloads\Compressed\dreamskrin\train_data_ads.csv'
df = pd.read_csv(data_path)

# Preprocess the dataset
def preprocess_data(df):
    label_encoders = {}
    categorical_columns = []
    for column in df.select_dtypes(include=['object']).columns:
        if column != 'label':
            le = LabelEncoder()
            df[column] = le.fit_transform(df[column])
            label_encoders[column] = le
            categorical_columns.append(column)
    
    # Separate features and label
    features = df.drop('label', axis=1)
    labels = df['label']
    
    # Use MinMaxScaler only on features
    scaler = MinMaxScaler(feature_range=(-1, 1))
    scaled_features = pd.DataFrame(scaler.fit_transform(features), columns=features.columns)
    
    # Combine scaled features and label
    df = pd.concat([scaled_features, labels], axis=1)
    
    return df, label_encoders, scaler, categorical_columns

# Preprocess the data
df, label_encoders, scaler, categorical_columns = preprocess_data(df)

# Separate features and labels
features = df.drop('label', axis=1)
labels = df['label']

# Ensure all data is float32
features = features.astype('float32')
labels = labels.astype('float32')

# Simplified Generator
def build_generator(latent_dim, output_dim):
    inputs = Input(shape=(latent_dim,))
    x = Dense(256, activation='relu')(inputs)
    x = Dense(512, activation='relu')(x)
    outputs = Dense(output_dim, activation='tanh')(x)
    return Model(inputs, outputs)

# Simplified Critic (Discriminator for WGAN)
def build_critic(input_dim):
    inputs = Input(shape=(input_dim,))
    x = Dense(512, activation='relu')(inputs)
    x = Dense(256, activation='relu')(x)
    outputs = Dense(1)(x)
    return Model(inputs, outputs)

# WGAN training function
@tf.function
def train_step(real_data, latent_dim, generator, critic, g_optimizer, c_optimizer):
    batch_size = tf.shape(real_data)[0]
    noise = tf.random.normal([batch_size, latent_dim])
    
    with tf.GradientTape() as c_tape, tf.GradientTape() as g_tape:
        generated_data = generator(noise, training=True)
        
        real_output = critic(real_data, training=True)
        fake_output = critic(generated_data, training=True)
        
        c_loss = tf.reduce_mean(fake_output) - tf.reduce_mean(real_output)
        g_loss = -tf.reduce_mean(fake_output)
        
        # Gradient penalty
        alpha = tf.random.uniform([batch_size, 1], 0., 1., dtype=tf.float32)
        interpolated = alpha * real_data + (1 - alpha) * generated_data
        with tf.GradientTape() as gp_tape:
            gp_tape.watch(interpolated)
            interp_output = critic(interpolated, training=True)
        grads = gp_tape.gradient(interp_output, interpolated)
        gp = tf.reduce_mean(tf.square(tf.sqrt(tf.reduce_sum(tf.square(grads), axis=1)) - 1))
        c_loss += 10 * gp
    
    c_gradients = c_tape.gradient(c_loss, critic.trainable_variables)
    g_gradients = g_tape.gradient(g_loss, generator.trainable_variables)
    
    c_optimizer.apply_gradients(zip(c_gradients, critic.trainable_variables))
    g_optimizer.apply_gradients(zip(g_gradients, generator.trainable_variables))
    
    return c_loss, g_loss

# Function to sample data and save
def sample_data(generator, latent_dim, epoch, labels, categorical_columns, samples=200000):
    noise = tf.random.normal([samples, latent_dim])
    generated_data = generator(noise, training=False).numpy()
    
    # Generate synthetic labels
    synthetic_labels = np.random.choice(labels, size=samples)
    
    # Create a DataFrame
    columns = list(features.columns) + ['label']
    synthetic_df = pd.DataFrame(np.column_stack((generated_data, synthetic_labels)), columns=columns)
    
    # Inverse transform the data (excluding the label column)
    synthetic_df.iloc[:, :-1] = scaler.inverse_transform(synthetic_df.iloc[:, :-1])
    
    for column in categorical_columns:
        # Clip values to the range of the encoder
        min_val, max_val = 0, len(label_encoders[column].classes_) - 1
        synthetic_df[column] = np.clip(synthetic_df[column].round(), min_val, max_val).astype(int)
        synthetic_df[column] = label_encoders[column].inverse_transform(synthetic_df[column])
    
    # Save the labeled synthetic dataset
    synthetic_df.to_csv(f"labeled_synthetic_data_epoch_{epoch}.csv", index=False)
    
    print(f"Saved synthetic data for epoch {epoch}")

# Training loop
def train_wgan(generator, critic, features, labels, latent_dim, categorical_columns, batch_size=64, epochs=100001, n_critic=5):
    g_optimizer = RMSprop(learning_rate=0.00005)
    c_optimizer = RMSprop(learning_rate=0.00005)
    
    for epoch in range(epochs):
        for _ in range(n_critic):
            idx = np.random.randint(0, features.shape[0], batch_size)
            real_data = tf.convert_to_tensor(features.iloc[idx].values, dtype=tf.float32)
            c_loss, _ = train_step(real_data, latent_dim, generator, critic, g_optimizer, c_optimizer)
        
        _, g_loss = train_step(real_data, latent_dim, generator, critic, g_optimizer, c_optimizer)
        
        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Critic Loss: {c_loss:.4f}, Generator Loss: {g_loss:.4f}")
        
        if epoch % 10000 == 0:
            sample_data(generator, latent_dim, epoch, labels, categorical_columns)

# Set random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# Define dimensions
latent_dim = 100
output_dim = features.shape[1]

# Build the WGAN
generator = build_generator(latent_dim, output_dim)
critic = build_critic(output_dim)

# Train the WGAN
train_wgan(generator, critic, features, labels, latent_dim, categorical_columns)
