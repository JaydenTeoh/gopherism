import subprocess
import time
import argparse
import threading
import os

# Set up argument parsing
parser = argparse.ArgumentParser(description="Download a file multiple times from a Gopher server and measure download times.")
parser.add_argument("-n", "--num-downloads", type=int, default=10, help="Number of times to download the file")
parser.add_argument("-p", "--port", type=int, default=443, help="Port number of the Gopher server (default: 443)")
parser.add_argument("-t", "--threads", type=int, default=5, help="Number of concurrent download threads")
args = parser.parse_args()

# File path and server URL
file_name = "LA4CS-Chapter-11.pdf"
if args.port == 443:  # using TLS port
    server_url = f"gophers://localhost:{args.port}/9/{file_name}"
else:  # using TCP port only
    server_url = f"gopher://localhost:{args.port}/9/{file_name}"

# Output target to discard data
output_target = "NUL" if os.name == "nt" else "/dev/null"

# Shared list for download times
download_times = []

# Thread-safe function to download the file and record time
def download_file(index):
    start_time = time.time()
    # Discard data by sending output to NUL (Windows) or /dev/null (Unix-based systems)
    subprocess.run(["curl", "-k", server_url, "-o", output_target])
    end_time = time.time()
    download_time = end_time - start_time
    download_times.append(download_time)
    # print(f"Download {index}: {download_time:.5f} seconds")

# Load test function using multithreading
def load_test():
    threads = []
    for i in range(1, args.num_downloads + 1):
        # Create and start a new thread for each download
        thread = threading.Thread(target=download_file, args=(i,))
        threads.append(thread)
        thread.start()

        # Wait for threads if we reach the thread limit
        if len(threads) >= args.threads:
            for t in threads:
                t.join()  # Ensure all threads are complete
            threads = []  # Reset the list of threads for the next batch

    # Wait for any remaining threads to finish
    for t in threads:
        t.join()

# Run the load test
start_test_time = time.time()
load_test()
end_test_time = time.time()

# Calculate average and total download times
average_time = sum(download_times) / len(download_times)
total_time = sum(download_times)

total_time = end_test_time - start_test_time
average_response_time = sum(download_times) / len(download_times) if download_times else 0

print(f"\nTotal test time: {total_time:.2f} seconds")
print(f"Average response time: {average_response_time:.2f} seconds")

"""
1000 requests, 1 thread:
Total test time: 279.07 seconds
Average response time: 0.28 seconds

1000 requests, 10 threads:
Total test time: 65.66 seconds
Average response time: 0.60 seconds

1000 requests, 100 threads:
Total test time: 80.70 seconds
Average response time: 6.57 seconds

1000 requests, 1000 threads:
Total test time: 159.71 seconds
Average response time: 153.84 seconds


"""