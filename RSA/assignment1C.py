import os
import math
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



#Fontes
#https://www.youtube.com/watch?v=D_PfV_IcUdA
#https://www.youtube.com/watch?v=IJwWJD5N_DY
#https://www.youtube.com/watch?v=9m8enHN13mw
#Criptografia e Segurança de Redes. 6º edição
#https://hrodriches.medium.com/encripta%C3%A7%C3%A3o-rsa-com-python-3-6d7620f167c2
#https://pt.linkedin.com/pulse/how-generate-rsa-key-pairs-python-simple-guide-secure-ribeiro-cissp-hjcye?tl=pt
#https://www.w3schools.com/python/ref_func_pow.asp

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

## Generate keys
privateKey = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048 
)
publicKey = privateKey.public_key()

## -- Used Gemini
## Used Gemini to figure out how to extract n, e, and d from the generated keys.
privateNumbers = privateKey.private_numbers()
publicNumbers = publicKey.public_numbers()
n = publicNumbers.n
e = publicNumbers.e
d = privateNumbers.d
## Gemini ends here

def encrypt(r, e, n):
    return pow(r, e, n)

def decrypt(c, d, n):
    return pow(c, d, n)


def enc_dec_test():
    results = [] # list for storing time use for encryption

    for size in FILE_SIZE:
        filename = f"{size}.bin"
        with open(DIRECTORY / f"{filename}", "rb") as f:
                message = f.read(); # Reads .bin files 

                time_list_enc = [] # list for storing time use for encryption
                time_list_dec = [] # list for storing time use for decryption

                for _ in range(repetitions):
                    timer(message, size, time_list_enc, False, rsa_cryptograph) # calls timer function to time the encryption process       

                # creating encrypted file for decrypt test
                enc_message = rsa_cryptograph(message, size, True) # encrypts the txt file for decryption test
               
                for _ in range(repetitions):
                    timer(enc_message, size, time_list_dec, None, rsa_decryptograph) # calls timer function to time the decryption process

                enc_mean, enc_std = calculate_stats(time_list_enc)
                dec_mean, dec_std = calculate_stats(time_list_dec)

                #Gemini use
                enc_mean, enc_std = calculate_stats(time_list_enc)
                dec_mean, dec_std = calculate_stats(time_list_dec)
                
               
                # back to seconds
                enc_time_sec = enc_mean / 1_000_000
                dec_time_sec = dec_mean / 1_000_000
                
                
                # Size in Megabytes 
                size_mb = size / (1024 * 1024)
                
                # Throughput (MB/s) = Size (MB) / Time (Seconds)
                enc_throughput_MBps = size_mb / enc_time_sec if enc_time_sec > 0 else 0
                dec_throughput_MBps = size_mb / dec_time_sec if dec_time_sec > 0 else 0
                # =========================================================

                results.append({ # appends dict of results to list. Will be used to create plot and csv 
                    "file_name": filename, 
                    "file_size_bytes": size,
                    "enc_mean": enc_mean, 
                    "enc_std": enc_std,
                    "enc_throughput_MBps": enc_throughput_MBps, # <-- Salvando Throughput
                    "dec_mean": dec_mean,
                    "dec_std": dec_std,
                    "dec_throughput_MBps": dec_throughput_MBps  # <-- Salvando Throughput
                }) 

                print(f"Encryption {filename} - Time: {enc_time_sec:.6f} seconds | Throughput: {enc_throughput_MBps:.4f} MB/s")
                print(f"Decryption {filename} - Time: {dec_time_sec:.6f} seconds | Throughput: {dec_throughput_MBps:.4f} MB/s")
                #Gemini end
                print(f"Encryption {filename} - Enc mean time: {enc_mean:.6f} microseconds, Std Dev: {enc_std:.6f} microseconds")
                print(f"Decryption {filename} - Dec mean time: {dec_mean:.6f} microseconds, Std Dev: {dec_std:.6f} microseconds")

    df = pd.DataFrame(results)

    return df



def rsa_cryptograph(mensagem, size, state):

    ##Generate r 
    r = os.urandom(32)
    r_int = int.from_bytes(r, byteorder='big')
    r_encrypt_int = encrypt(r_int, e, n)
    r_encrypt = r_encrypt_int.to_bytes(256, byteorder='big')
    tamanho_bloco = 32

    cipher_text = bytearray(r_encrypt)
    for i in range(0, size, tamanho_bloco):
        counter = i//tamanho_bloco #not i because we want block 1, block 2 ... not block 1, block 32..
        mensagemDividida = mensagem[i: i + tamanho_bloco]
        r_atual = counter.to_bytes(4, byteorder='big') + r
        r_sha = hashlib.sha256(r_atual).digest() #H(i, r)
        block_cipher = bytes(a ^ b for a, b in zip(mensagemDividida, r_sha)) #Used Gemini for this cycle
        cipher_text.extend(block_cipher) #We're using `extend()` instead of `append()` because we're adding multiple bytes at once.
    encrypted_msg = bytes(cipher_text)

    if state ==  True: # if state is true, then an encrypted file will be made (for decryption test)
        if not os.path.exists("enc_data"):
            os.makedirs("enc_data")
        with open(f"enc_data/{size}_rsa_encrypted.bin", "wb") as f:
            f.write(encrypted_msg)
            f.close()
    
    return bytes(encrypted_msg)








def rsa_decryptograph(cipher, size, state):
    r_cipher_bytearray = cipher[:256] # cipher r
    cipher_text = cipher[256:] #cipher text without r
    r_cipher_int = int.from_bytes(r_cipher_bytearray, byteorder='big')
    r_int = decrypt(r_cipher_int, d, n)
    r = r_int.to_bytes(32, byteorder='big')
    tamanho_bloco = 32

    plain_text = bytearray()

    for i in range(0, len(cipher_text), tamanho_bloco):
        counter = i//tamanho_bloco
        mensagemDividida = cipher_text[i: i + tamanho_bloco]
        r_atual = counter.to_bytes(4, byteorder='big') + r
        r_sha = hashlib.sha256(r_atual).digest() #H(i, r)
        block_decipher = bytes(a ^ b for a, b in zip(mensagemDividida, r_sha)) #Used Gemini for this cycle
        plain_text.extend(block_decipher) #We're using `extend()` instead of `append()` because we're adding multiple bytes at once.
    decrypted_msg = bytes(plain_text)

    if state ==  True: # if state is true, then an encrypted file will be made (for decryption test)
        if not os.path.exists("dec_data"):
            os.makedirs("dec_data")
        with open(f"dec_data/{size}_rsa_decrypted.bin", "wb") as f:
            f.write(decrypted_msg)
            f.close()
    
    return bytes(decrypted_msg)

        

    
    
    
def timer(message, size, time_list, state, function):

    for _ in range(3): # warmup function :)
        function(message, size, state)

    time1 = timeit.default_timer() # timer starts here
    function(message, size, state)
    time2 = timeit.default_timer() # timer ends here

    total_time = (time2 - time1)* 1_000_000 #time is in microsseconds
    time_list.append(total_time) # appends time use to list





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
        label="RSA - Encrypt"
    )

    plt.errorbar(
        df["file_name"],
        df["dec_mean"],
        yerr=df["dec_std"],
        marker="s",
        capsize=0,
        label="RSA - Decrypt"
    )

    plt.xticks(
        df["file_name"], 
        labels=df["file_name"], 
    )

    plt.yscale("log") # using logarithmic scale for better visualization of time differences across file sizes
    # plt.xscale("linear")
    plt.xlabel("File size (bytes)")
    plt.ylabel("Time (microseconds)")
    plt.title("RSA - 2048  Encryption/Decryption Time Use")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.tight_layout()

    plot_path = "results/RSA_plot.png"
    plt.savefig(plot_path, dpi=300)
    plt.show()

    print(f"Saved plot to: {plot_path}")    


def save_results(df: pd.DataFrame) -> None:
    if not os.path.exists("results"):
        os.makedirs("results", exist_ok=True)

    csv_path = "results/RSA_results.csv"
    df.to_csv(csv_path, index=False)

    print("\nBenchmark results:")
    print(df.to_string(index=False))
    print(f"\nSaved CSV to: {csv_path}")

### ------ ChatGPT ends here




##For benchmarking
#the number of public/private-key operations(key generation) per second
def rsa_key_genetation(number):
    time_start = timeit.default_timer()
    for i in range(number):
        rsa.generate_private_key(public_exponent=65537, key_size=2048 )
    time_end = timeit.default_timer()
    total_time = time_end - time_start
    velocity = number/total_time
    print(f"{number} keys were generated in {total_time:.4f} seconds.")
    print(f"{velocity:.2f} keys per second.")

    




if __name__ == "__main__":
    rsa_key_genetation(10) #escolher o melhor número de iterações
    generate_random_files()
    result = enc_dec_test()
    plot_results(result) # plotting of results to graph
    save_results(result) # saving of results to csv file








