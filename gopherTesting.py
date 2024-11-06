import subprocess
import time
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser(description="Download a file multiple times from a Gopher server and measure download times.")
parser.add_argument("-n", "--num-downloads", type=int, default=10, help="Number of times to download the file")
parser.add_argument("-p", "--port", type=int, default=443, help="Port number of the Gopher server (default: 443)")
args = parser.parse_args()

# File path and server URL
file_name = "LA4CS-Chapter-11.pdf"
server_url = f"gophers://localhost:{args.port}/9/{file_name}"

download_times = []
num_downloads = args.num_downloads

# Download the file multiple times
for i in range(1, num_downloads + 1):
    start_time = time.time()
    subprocess.run(["curl", "-k", server_url, "-o", file_name])
    end_time = time.time()
    download_time = end_time - start_time
    download_times.append(download_time)
    print(f"Download {i}: {download_time:.5f} seconds")

# Calculate average and total download times
average_time = sum(download_times) / num_downloads
total_time = sum(download_times)

print(f"\nAverage download time for {num_downloads} downloads: {average_time:.5f} seconds")
print(f"Total download time: {total_time:.5f} seconds")
