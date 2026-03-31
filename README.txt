Cryptographic Operations Benchmark 

  

This repository contains multiple Python scripts for benchmarking cryptographic operations, specifically focusing on encryption and decryption using RSA, AES and SHA modes. The scripts generate random files of varying sizes, perform encryption/decryption, and analyse the performance. 

  

Files: 

'assignment1B.py' : benchmarks standardized symmetric encryption using AES-256 in Counter (CTR) mode. 
'assignment1C.py' : benchmarks hybrid stream cypher that uses RSA on a random integer and XOR's the hash to the plaintext 
'assignment1D.py' : benchmarks SHA-256 digests. 

  

Prerequisites & Installation: 

to run the code, you need python 3.8+ and some external libraries. 
to instal the libraries run on the bash: 
  pip install cryptography pandas matplotlib 

  

How to run: 

you can run both files independenty on the terminal with  
AES Benchmark 
  python assignmentB.py 

RSA Benchmark 
  python assignment1C.py 

SHA Benchmark 
  python assignment1D.py 

  

Output: 

the scripts will 
  print the mean, median, Throughput and standard deviation of the encryption and decryption. 
  save a line graph and a breakdown in cvs to the results folder. 
  save the binary files used in the text_files folder. 

  

Functions: 

Mutual functions 

  generate_random_files() : generates random files of 8,64,512,4096,32768,262144,2097152 bytes 

  timer(message, size, time_list, state, function) : given a message, the message size, a list of times, a state(used for the functions decrypt), and a function that receives a message, the message size and a state; it appends to the list the time it takes to run the function. 

  calculate_stats(times_us): given a list of times it calculates the mean, median and standard deviation of the values in the list. 

  enc_dec_test() : generates a dictionary of the benchmark values for encryption and decryption (or only encryption in 'assignment1D.py') 

  plot_results(df: pd.DataFrame) -> None : plots the results of the dictionary in a graph in witch the x axis is the file size and the y axis is the time to run. 

  save_results(df: pd.DataFrame) -> None:  saves the results of the benchmark in a results folder. 

assignment1B.py 

  CTR_256_encrypt(message, size, state): given a message, the size of the message and a state, encrypts the message with ASE in counter mode, the state is used to save the results for decryption 

  CTR_256_decrypt(encrypted_message, size, state): given a message, the size of the message and a state, decrypts the message in ASE in counter mode to plain text 

assignment1C.py 

  encrypt(r, e, n) / decrypt(c, d, n) : given the number in a key return the power of them. 

  rsa_cryptograph(mensagem, size, state): given a message, the size of the message and a state, encrypts the message with an RSA hybrid that generates a random r, uses RSA on R , gets the Hash of the cypher r and XOR's it with the plaintext 

  rsa_decryptograph(cipher, size, state): given a message, the size of the message and a state, decrypts the message in an RSA hybrid by getting the crypted r hash, hashing again, using the private key to decrypt the r and XOR's it with the cypher text 

  rsa_key_genetation(number): given a number generates number keys to calculate how many keys the algorith can generate per second.

assignment1D.py 

  sha_cryptograph(mensagem, size, state): given a message, the size of the message and a state, encrypts the message with SHA-256
