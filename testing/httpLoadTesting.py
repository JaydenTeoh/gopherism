import subprocess
import threading
import time
import argparse

# Argument parsing to choose HTTP or HTTPS
parser = argparse.ArgumentParser(description="Load test HTTP or HTTPS server using curl.")
parser.add_argument("-tls", action="store_true", help="Use HTTPS if this flag is set; otherwise, HTTP.")
args = parser.parse_args()

# Server URL to test (adjust based on the -tls flag)
if args.tls:
    URL = "https://127.0.0.1:8443/download/LA4CS-Chapter-11.pdf"
else:
    URL = "http://127.0.0.1:8080/download/LA4CS-Chapter-11.pdf"

# Number of concurrent threads and requests per thread
NUM_THREADS = 1000  # Number of concurrent threads
REQUESTS_PER_THREAD = 10  # Number of requests each thread will make
results = []

# Function to make requests using curl and record response times and file size
def make_requests():

    for _ in range(REQUESTS_PER_THREAD):
        try:
            # Build the curl command

            # Run the curl command and capture the output

            start_time = time.time()
            # Discard data by sending output to NUL (Windows) or /dev/null (Unix-based systems)
            subprocess.run(["curl", "-k", URL, "-o", "NUL"])

            end_time = time.time()
            download_time = end_time - start_time
            results.append(download_time)

        except subprocess.CalledProcessError as e:
            print(f"Request failed: {e}")

# Function to create and start threads
def load_test():
    threads = []

    # Create threads
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=make_requests)
        threads.append(thread)

    # Start threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

# Run the load test
start_test_time = time.time()
load_test()
end_test_time = time.time()

# Calculate total time taken and average response time
total_time = end_test_time - start_test_time
average_response_time = sum(results) / len(results) if results else 0

print(f"\nTotal test time: {total_time:.2f} seconds")
print(f"Average response time: {average_response_time:.2f} seconds")
print(f"Total requests completed: {len(results)}")
