import os
import statistics
import time
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# ----------------------------
# Configuration
# ----------------------------

FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]
REPETITIONS = 100
DATA_DIR = Path("text_files")
RESULTS_DIR = Path("results")

KEY = os.urandom(32)   # AES-256
IV = os.urandom(16)    # 16 bytes for AES block size


# ----------------------------
# File generation
# ----------------------------

def generate_random_files(directory: Path, file_sizes: list[int]) -> None:
    """Generate random binary files of the given sizes."""
    directory.mkdir(parents=True, exist_ok=True)

    for size in file_sizes:
        file_path = directory / f"file_{size}.bin"
        with open(file_path, "wb") as f:
            f.write(os.urandom(size))


# ----------------------------
# AES-256 CTR
# ----------------------------

def aes_ctr_encrypt(message: bytes, key: bytes, iv: bytes) -> bytes:
    """Encrypt bytes using AES-256 in CTR mode."""
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    encryptor = cipher.encryptor()
    return encryptor.update(message) + encryptor.finalize()


def aes_ctr_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """Decrypt bytes using AES-256 in CTR mode."""
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


# ----------------------------
# Benchmark helpers
# ----------------------------

def benchmark_operation(func, repetitions: int) -> list[float]:
    """
    Run a function multiple times and return execution times in microseconds.
    """
    times_us = []

    for _ in range(repetitions):
        start = time.perf_counter_ns()
        func()
        end = time.perf_counter_ns()

        elapsed_us = (end - start) / 1000.0
        times_us.append(elapsed_us)

    return times_us


def summarize_times(times_us: list[float]) -> tuple[float, float]:
    """Return mean and standard deviation of timing values."""
    mean_us = statistics.mean(times_us)
    std_us = statistics.stdev(times_us) if len(times_us) > 1 else 0.0
    return mean_us, std_us


# ----------------------------
# Main benchmark
# ----------------------------

def run_aes_ctr_benchmark() -> pd.DataFrame:
    """
    Benchmark AES-256 CTR encryption and decryption for all files.
    Returns a pandas DataFrame with results.
    """
    results = []

    for size in FILE_SIZES:
        file_path = DATA_DIR / f"file_{size}.bin"

        with open(file_path, "rb") as f:
            plaintext = f.read()

        ciphertext = aes_ctr_encrypt(plaintext, KEY, IV)

        # Benchmark encryption
        enc_times = benchmark_operation(
            lambda: aes_ctr_encrypt(plaintext, KEY, IV),
            REPETITIONS
        )
        enc_mean, enc_std = summarize_times(enc_times)

        # Benchmark decryption
        dec_times = benchmark_operation(
            lambda: aes_ctr_decrypt(ciphertext, KEY, IV),
            REPETITIONS
        )
        dec_mean, dec_std = summarize_times(dec_times)

        # Optional correctness check
        recovered = aes_ctr_decrypt(ciphertext, KEY, IV)
        assert recovered == plaintext, f"Decryption failed for file size {size}"

        results.append({
            "file_size_bytes": size,
            "encrypt_mean_us": enc_mean,
            "encrypt_std_us": enc_std,
            "decrypt_mean_us": dec_mean,
            "decrypt_std_us": dec_std,
        })

    df = pd.DataFrame(results)
    return df


# ----------------------------
# Save + visualize
# ----------------------------

def save_results(df: pd.DataFrame) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = RESULTS_DIR / "aes_ctr_results.csv"
    df.to_csv(csv_path, index=False)

    print("\nBenchmark results:")
    print(df.to_string(index=False))
    print(f"\nSaved CSV to: {csv_path}")


def plot_results(df: pd.DataFrame) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))

    plt.errorbar(
        df["file_size_bytes"],
        df["encrypt_mean_us"],
        yerr=df["encrypt_std_us"],
        marker="o",
        capsize=4,
        label="AES-CTR Encrypt"
    )

    plt.errorbar(
        df["file_size_bytes"],
        df["decrypt_mean_us"],
        yerr=df["decrypt_std_us"],
        marker="s",
        capsize=4,
        label="AES-CTR Decrypt"
    )

    plt.xscale("log")
    plt.xlabel("File size (bytes)")
    plt.ylabel("Time (microseconds)")
    plt.title("AES-256 CTR Encryption/Decryption Performance")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.tight_layout()

    plot_path = RESULTS_DIR / "aes_ctr_plot.png"
    plt.savefig(plot_path, dpi=300)
    plt.show()

    print(f"Saved plot to: {plot_path}")


# ----------------------------
# Run
# ----------------------------

if __name__ == "__main__":
    generate_random_files(DATA_DIR, FILE_SIZES)
    df_results = run_aes_ctr_benchmark()
    save_results(df_results)
    plot_results(df_results)