import subprocess
import time

# Set the file path and server URL
file_name = "LA4CS-Chapter-11.pdf"
server_url = "gophers://localhost:443/9/LA4CS-Chapter-11.pdf"

download_times = []

# Download the same file 10 times
for i in range(10):
    start_time = time.time()
    subprocess.run(["curl", "-k", server_url, "-o", file_name])
    end_time = time.time()
    download_time = end_time - start_time
    download_times.append(download_time)
    print(f"Download {i + 1}: {download_time:.2f} seconds")

#     # Download the same file 100 times
# for i in range(10):
#     start_time = time.time()
#     subprocess.run(["curl", "-k", server_url, "-o", file_name])
#     end_time = time.time()
#     download_time = end_time - start_time
#     download_times.append(download_time)
#     print(f"Download {i + 1}: {download_time:.2f} seconds")

#     # Download the same file 1000 times
# for i in range(1000):
#     start_time = time.time()
#     subprocess.run(["curl", "-k", server_url, "-o", file_name])
#     end_time = time.time()
#     download_time = end_time - start_time
#     download_times.append(download_time)
#     print(f"Download {i + 1}: {download_time:.2f} seconds")

print("\nDownload times for each attempt:", download_times)
print("Average download time:", sum(download_times) / len(download_times))
