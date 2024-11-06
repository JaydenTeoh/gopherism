import subprocess
import time
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser(description="Download a file multiple times from an HTTP server and measure download times.")
parser.add_argument("-n", "--num-downloads", type=int, default=10, help="Number of times to download the file")
parser.add_argument("-p", "--port", type=int, default=80, help="Port number of the HTTP server (default: 80)")
parser.add_argument("-f", "--filename", type=str, default="LA4CS-Chapter-11.pdf", help="Name of the file to download")
args = parser.parse_args()

# Construct the URL for downloading the file
server_url = f"https://localhost:{args.port}/download/{args.filename}"

download_times = []
num_downloads = args.num_downloads

# Download the file multiple times
for i in range(1, num_downloads + 1):
    start_time = time.time()
    subprocess.run(["curl","-k" ,"-O", server_url])
    end_time = time.time()
    download_time = end_time - start_time
    download_times.append(download_time)
    print(f"Download {i}: {download_time:.5f} seconds")

# Calculate average and total download times
average_time = sum(download_times) / num_downloads
total_time = sum(download_times)

print(f"\nAverage download time for {num_downloads} downloads: {average_time:.5f} seconds")
print(f"Total download time: {total_time:.5f} seconds")
