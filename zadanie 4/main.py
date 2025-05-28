import os

import numpy as np
import pygame
import scipy.io.wavfile as wavfile
import sounddevice as sd
from scipy.signal import resample

# Configuration
SAMPLE_RATES = [8000, 22050, 44100, 48000]  # Sampling frequencies (Hz)
BIT_DEPTHS = [8, 16]  # Bit depths for audio
RECORD_DURATION = 3  # Recording duration in seconds
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "recordings")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Reference audio file
REFERENCE_FILE = "original_48000Hz_16bit.wav"
REFERENCE_FILEPATH = os.path.join(OUTPUT_FOLDER, REFERENCE_FILE)

# Record high-quality reference audio
def capture_reference_audio():
    print("Capturing reference audio at 48000 Hz, 16-bit...")
    audio_data = sd.rec(int(RECORD_DURATION * 48000), samplerate=48000, channels=1, dtype='float32')
    sd.wait()  # Wait for recording to complete
    scaled_audio = np.clip(audio_data * 32767, -32768, 32767).astype(np.int16)
    wavfile.write(REFERENCE_FILEPATH, 48000, scaled_audio)
    print(f"Saved reference audio to: {REFERENCE_FILEPATH}")
    return audio_data.flatten()

# Convert audio to specified sample rate and bit depth
def process_audio(original_audio, source_rate, target_rate, bit_depth):
    # Resample to target sample rate
    target_samples = int(len(original_audio) * target_rate / source_rate)
    resampled_audio = resample(original_audio, target_samples)

    # Adjust bit depth
    if bit_depth == 8:
        converted_audio = np.clip(resampled_audio * 127.5 + 127.5, 0, 255).astype(np.uint8)
    else:  # 16-bit
        converted_audio = np.clip(resampled_audio * 32767, -32768, 32767).astype(np.int16)

    output_file = f"audio_{target_rate}Hz_{bit_depth}bit.wav"
    output_path = os.path.join(OUTPUT_FOLDER, output_file)
    wavfile.write(output_path, target_rate, converted_audio)
    print(f"Saved converted audio: {output_path}")

# Calculate Signal-to-Noise Ratio (SNR)
def calculate_snr(ref_path, test_path):
    ref_rate, ref_data = wavfile.read(ref_path)
    test_rate, test_data = wavfile.read(test_path)

    # Resample test audio to match reference sample rate
    if test_rate != ref_rate:
        target_samples = len(ref_data)
        test_data = resample(test_data, target_samples)

    # Convert to float64 for precision
    ref_data = ref_data.astype(np.float64)
    test_data = test_data.astype(np.float64)

    # Truncate to same length
    min_length = min(len(ref_data), len(test_data))
    ref_data = ref_data[:min_length]
    test_data = test_data[:min_length]

    # Compute noise and SNR
    noise = ref_data - test_data
    signal_power = np.mean(ref_data ** 2)
    noise_power = np.mean(noise ** 2)

    if noise_power == 0:
        return float('inf')
    return 10 * np.log10(signal_power / noise_power)

# Play audio using pygame
def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Wait for playback to finish

# Main execution
if __name__ == "__main__":
    # Initialize pygame mixer
    pygame.init()

    # Record reference audio
    original_audio = capture_reference_audio()

    # Convert to various formats
    for rate in SAMPLE_RATES:
        for depth in BIT_DEPTHS:
            output_file = f"audio_{rate}Hz_{depth}bit.wav"
            output_path = os.path.join(OUTPUT_FOLDER, output_file)
            if output_path != REFERENCE_FILEPATH:
                process_audio(original_audio, 48000, rate, depth)

    # Analyze SNR and summarize results
    results = []
    for rate in SAMPLE_RATES:
        for depth in BIT_DEPTHS:
            audio_file = f"audio_{rate}Hz_{depth}bit.wav"
            audio_path = os.path.join(OUTPUT_FOLDER, audio_file)

            if audio_path == REFERENCE_FILEPATH:
                snr = "Reference"
                quality = "Original recording"
            else:
                snr = calculate_snr(REFERENCE_FILEPATH, audio_path)
                if snr < 20:
                    quality = "Significant quality loss"
                elif snr < 30:
                    quality = "Moderate quality"
                else:
                    quality = "High quality"

            results.append((audio_file, rate, f"{depth}-bit", snr, quality))

    # Display summary
    print("\n--- Audio Quality Summary ---")
    for file, rate, depth, snr, quality in results:
        if isinstance(snr, float):
            print(f"{file}: {rate} Hz, {depth}, SNR = {snr:.2f} dB -> {quality}")
        else:
            print(f"{file}: {rate} Hz, {depth}, SNR = {snr} -> {quality}")

    # Playback all recordings
    print("\n--- Playing Audio Files (Digital-to-Analog Simulation) ---")
    for file, _, _, _, _ in results:
        file_path = os.path.join(OUTPUT_FOLDER, file)
        print(f"Playing: {file}")
        play_audio(file_path)