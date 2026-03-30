import os

from os import urandom
from binascii import hexlify
from time import time
from cryptography.hazmat.primitives.asymmetric import rsa
import hashlib
import timeit
import statistics
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


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



def timer(message, size, time_list, state, function):

    for i in range(3):
        function(message, size, state)

    time1 = timeit.default_timer() # timer starts here
    function(message, size, state)
    time2 = timeit.default_timer() # timer ends here

    total_time = (time2 - time1)* 1_000_000 #time is in microsseconds
    time_list.append(total_time) # appends time use to list


def enc_test():
    results = [] # list for storing time use for encryption

    for size in FILE_SIZE:
        filename = f"{size}.bin"
        with open(DIRECTORY / f"{filename}", "rb") as f:
                message = f.read(); # Reads .bin files 

                time_list_enc = [] # list for storing time use for encryption
                

                for _ in range(repetitions):
                    timer(message, size, time_list_enc, False, sha_cryptograph) # calls timer function to time the encryption process       

                enc_mean, enc_std = calculate_stats(time_list_enc)
                enc_time_sec = enc_mean / 1_000_000
                size_mb = size / (1024 * 1024)
                enc_throughput_MBps = size_mb / enc_time_sec if enc_time_sec > 0 else 0
                

                results.append({ # appends dict of results to list. Will be used to create plot and csv 
                    "file_name": filename, 
                    "file_size_bytes": size,
                    "enc_mean": enc_mean, 
                    "enc_std": enc_std,
                    "enc_throughput_MBps": enc_throughput_MBps, # <-- Salvando Throughput
                    
                })
                
                print(f"SHA-256 Digest {filename} - Time: {enc_time_sec:.6f} seconds | Throughput: {enc_throughput_MBps:.4f} MB/s")
                print(f"SHA-256 Digest {filename} - Enc mean time: {enc_mean:.6f} microseconds, Std Dev: {enc_std:.6f} microseconds")
                

    df = pd.DataFrame(results)

    return df




def sha_cryptograph(mensagem, size, state):


    encrypted_msg = hashlib.sha256(mensagem).digest() 

    if state ==  True: 
        if not os.path.exists("enc_data"):
            os.makedirs("enc_data")
        with open(f"enc_data/{size}_sha_encrypted.bin", "wb") as f:
            f.write(encrypted_msg)
            f.close()
    
    return bytes(encrypted_msg)


def calculate_stats(times_us):
    mean_us = statistics.mean(times_us) # creating mean of times in list
    std_us = statistics.stdev(times_us) # creating standard deviation of times in list
    return mean_us, std_us

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
        label="SHA-256 Digest"
    )

   

    plt.xticks(
        df["file_name"], 
        labels=df["file_name"], 
    )

    plt.yscale("log") # using logarithmic scale for better visualization of time differences across file sizes
    # plt.xscale("linear")
    plt.xlabel("File size (bytes)")
    plt.ylabel("Time (microseconds)")
    plt.title("SHA-256 Digest Time Use")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.tight_layout()

    plot_path = "results/SHA256_plot.png"
    plt.savefig(plot_path, dpi=300)
    plt.show()

    print(f"Saved plot to: {plot_path}")    


def save_results(df: pd.DataFrame) -> None:
    if not os.path.exists("results"):
        os.makedirs("results", exist_ok=True)

    csv_path = "results/SHA256_results.csv"
    df.to_csv(csv_path, index=False)

    print("\nBenchmark results:")
    print(df.to_string(index=False))
    print(f"\nSaved CSV to: {csv_path}")

### ------ ChatGPT ends here

if __name__ == "__main__":
    generate_random_files()
    result = enc_test()
    plot_results(result) # plotting of results to graph
    save_results(result) # saving of results to csv file
