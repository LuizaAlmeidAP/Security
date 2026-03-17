import os


# Used CHATGPT
file_sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]
files = {}

for size in file_sizes:
    filename = f"file_{size}.bin"
    with open(filename, "wb") as f:
        f.write(os.urandom(size))
    files[size] = filename
# 

