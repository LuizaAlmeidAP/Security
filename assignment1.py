import os
from os import urandom
from binascii import hexlify
from time import time
from cryptography .hazmat. primitives . ciphers import Cipher , algorithms , modes
import timeit
import statistics
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import pyperf
import time

key = urandom(32)
iv = urandom(16)
repetitions = 100
DIRECTORY = Path('text_files')
FILE_SIZE = [8, 64, 512, 4096, 32768, 262144, 2097152]

## -- Used ChatGPT
## USed the os.urandom function to generate random bytes and create files of specified sizes
def generate_random_files():
    # files = {}
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    for size in FILE_SIZE:
        filename = DIRECTORY / f"{size}.bin"
        with open(filename, "wb") as f:
            f.write(os.urandom(size))
        # files[size] = filename
## --- ChatGPT ends here 

def enc_dec_test():
    results = [] # list for storing time use for encryption

    for size in FILE_SIZE:
        filename = f"{size}.bin"
        with open(DIRECTORY / f"{filename}", "rb") as f:
                message = f.read(); # Reads .bin files 

                time_list_enc = [] # list for storing time use for encryption
                time_list_dec = [] # list for storing time use for decryption

                for _ in range(repetitions):
                    timer(message, size, time_list_enc, False, CTR_256_encrypt) # calls timer function to time the encryption process       

                # creating encrypted file for decrypt test
                enc_message = CTR_256_encrypt(message, size, True) # encrypts the txt file for decryption test
               
                for _ in range(repetitions):
                    timer(enc_message, None, time_list_dec, None, CTR_256_decrypt) # calls timer function to time the decryption process

                enc_mean, enc_std, enc_median = calculate_stats(time_list_enc)
                dec_mean, dec_std, dec_median = calculate_stats(time_list_dec)
                enc_throughput = (size / enc_mean) / (1024 * 1024)
                dec_throughput = (size / dec_mean) / (1024 * 1024)
                
                results.append({ # appends dict of results to list. Will be used to create plot and csv 
                    "file_name": filename, 
                    "enc_mean": enc_mean,
                    "enc_median": enc_median, 
                    "enc_std": enc_std,
                    "enc_throughput": enc_throughput,
                    "dec_mean": dec_mean,
                    "dec_median": dec_median,
                    "dec_std": dec_std,
                    "dec_throughput": dec_throughput}) 

                print(f"Encryption {filename} - Enc mean time: {enc_mean:.6f} seconds, Enc median time: {enc_median:.6f} seconds, Std Dev: {enc_std:.6f} seconds, Enc throughput: {enc_throughput} MB/s")
                print(f"Decryption {filename} - Dec mean time: {dec_mean:.6f} seconds, Dec median time: {dec_median:.6f} seconds, Std Dev: {dec_std:.6f} seconds, Dec throughput: {enc_throughput} MB/s")

    df = pd.DataFrame(results)

    return df

def CTR_256_encrypt(message, size, state): # Encryption with AES-256 CTR
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    encryptor = cipher.encryptor()
    encrypted_msg = encryptor.update((message)) + encryptor.finalize()

    if state ==  True: # if state is true, then an encrypted file will be made (for decryption test)
        if not os.path.exists("enc_data"):
            os.makedirs("enc_data")
        with open(f"enc_data/{size}_encrypted.bin", "wb") as f:
            f.write(encrypted_msg)
            f.close()
        return encrypted_msg

def CTR_256_decrypt(encrypted_message, size, state): # decryption with AES-256 CTR
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    decryptor = cipher.decryptor()
    decryptor.update(encrypted_message) + decryptor.finalize()


def timer(message, size, time_list, state, function):

    for _ in range(10): # warmup function :)
        function(message, size, state)

    time1 = time.perf_counter() # timer starts here
    function(message, size, state)
    time2 = time.perf_counter() # timer ends here

    time_list.append(time2 - time1) # appends time use to list



def calculate_stats(times_us):
    mean_us = statistics.mean(times_us) # creating mean of times in list
    std_us = statistics.stdev(times_us) # creating standard deviation of times in list
    median_us = statistics.median(times_us) # creating median of time in list
    return mean_us, std_us, median_us


### ---- Chatgpt
def plot_results(df: pd.DataFrame) -> None:
    if not os.path.exists("results"):
        os.makedirs("results", exist_ok=True)

    plt.figure(figsize=(10, 6))

    plt.errorbar(
        df["file_name"],
        df["enc_mean"],
        yerr=df["enc_std"],
        marker="o",
        capsize=0,
        label="AES-CTR Encrypt"
    )

    plt.errorbar(
        df["file_name"],
        df["dec_mean"],
        yerr=df["dec_std"],
        marker="s",
        capsize=0,
        label="AES-CTR Decrypt"
    )

    plt.xticks(
        df["file_name"], 
        labels=df["file_name"], 
    )

    plt.yscale("log") # using logarithmic scale for better visualization of time differences across file sizes
    # plt.xscale("linear")
    plt.xlabel("File size (bytes)")
    plt.ylabel("Time (microseconds)")
    plt.title("AES-256 CTR Encryption/Decryption Time Use")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.tight_layout()

    plot_path = "results/aes_ctr_plot.png"
    plt.savefig(plot_path, dpi=300)
    plt.show()

    print(f"Saved plot to: {plot_path}")    


def save_results(df: pd.DataFrame) -> None:
    if not os.path.exists("results"):
        os.makedirs("results", exist_ok=True)

    csv_path = "results/aes_ctr_results.csv"
    df.to_csv(csv_path, index=False)

    print("\nBenchmark results:")
    print(df.to_string(index=False))
    print(f"\nSaved CSV to: {csv_path}")

### ------ ChatGPT ends here

if __name__ == "__main__":
    generate_random_files()
    result = enc_dec_test()
    plot_results(result) # plotting of results to graph
    save_results(result) # saving of results to csv file
