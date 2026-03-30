This repository contains two Python scripts for benchmarking cryptographic operations, specifically focusing on encryption and decryption using RSA and AES mode. The scripts generate random files of varying sizes, perform encryption/decryption, and analyze the performance.

Files:
'assignment1.py'  : benchmarks standardized symmetric encryption using AES-256 in Counter (CTR) mode.
'assignment1c.py' : benchmarks hybrid stream cypher that uses RSA on a random integer and XOR's the hash to the plaintext

Prerequisites & Installation:
to run the code you need python 3.8+ and some external libraries.
to instal the libraries run on the bash:
pip install cryptography pandas matplotlib

How to run:
you can run both of the files independenty on the terminal with 
AES Benchmark
python assignment1.py
RSA Benchmark
python assignment1c.py

Output:
the scripts will
print the mean, median, Throughput and standard deviation of the encryption and decryption.
save a line graph and a breakdown in cvs to the results folder.
save the binary files used in the text_files folder.