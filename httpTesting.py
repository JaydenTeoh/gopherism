import requests
import time

# Server URL and file to download
server_url = 'https://localhost:8443/download/LA4CS-Chapter-11.pdf'  # Replace with your actual file
download_count = 100
file_name = 'LA4CS-Chapter-11.pdf'

# List to store download times
download_times = []

for i in range(download_count):
    start_time = time.time()  # Record start time
    try:
        response = requests.get(server_url, verify=False)
        response.raise_for_status()  # Ensure we got a successful response

        # Discard the content to avoid storing it 1000 times
        end_time = time.time()  # Record end time
        download_time = end_time - start_time
        download_times.append(download_time)
        print(f"Download {i + 1}: {download_time:.5f} seconds")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during download {i + 1}: {e}")

# Calculate average download time
average_time = sum(download_times) / len(download_times)
print(f"\nAverage download time for {download_count} downloads: {average_time:.5f} seconds\n")
print(f"Total download time: {sum(download_times):.5f} seconds")
