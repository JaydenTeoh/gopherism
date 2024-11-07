import requests
import threading
import time

# Server URL to test
URL = "https://127.0.0.1:8443/download/LA4CS-Chapter-11.pdf"
NUM_THREADS = 1  # Number of concurrent threads
REQUESTS_PER_THREAD = 1000  # Number of requests each thread will make
results = []

# Function to make requests and record response times
def make_requests():
    for _ in range(REQUESTS_PER_THREAD):
        try:
            start_time = time.time()
            # Set stream=True to avoid downloading the file content
            response = requests.get(URL, verify=False, stream=True)
            end_time = time.time()
            
            # Calculate response time
            response_time = end_time - start_time
            results.append(response_time)

            # Check if the request was successful
            if response.status_code == 200:
                print(f"Request successful: {response.status_code} | Response Time: {response_time:.2f} seconds")
            else:
                print(f"Request failed: {response.status_code}")
            
            # Close the connection without reading content
            response.close()

        except requests.exceptions.RequestException as e:
            print(f"Request exception: {e}")


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

"""
1 thread, 1000 requests each
Total test time: 63.33 seconds
Average response time: 0.06 seconds
Total requests completed: 1000

10 threads, 100 requests each
Total test time: 26.16 seconds
Average response time: 0.22 seconds
Total requests completed: 1000

100 threads, 10 requests each
Total test time: 26.65 seconds
Average response time: 1.12 seconds
Total requests completed: 1000

1000 threads, 1 request each
Total test time: 38.33 seconds
Average response time: 0.70 seconds
Total requests completed: 1000

"""