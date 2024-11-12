import subprocess
import os

# URLs for HTTP and HTTPS
HTTP_URL = "gopher://localhost:70/9/LA4CS-Chapter-11.pdf"
HTTPS_URL = "gophers://localhost:443/9/LA4CS-Chapter-11.pdf"

# Determine the appropriate null device based on OS
output_target = "NUL" if os.name == "nt" else "/dev/null"

# Function to test bandwidth using curl
def test_bandwidth(url, use_https=False):
    # Build the curl command
    curl_command = [
        "curl",
        "-o", output_target,        # Discard the downloaded file
        "-s",                       # Silent mode
        "-w", "%{time_total} %{size_download}",  # Output time and file size
        url
    ]

    # Add '-k' flag to ignore certificate errors for self-signed HTTPS
    if use_https:
        curl_command.insert(1, "-k")

    # Run the curl command and capture output
    result = subprocess.run(curl_command, capture_output=True, text=True)
    
    # Check if result.stdout is not None before attempting to strip
    if result.stdout is None:
        print("Error: curl command did not produce any output.")
        print(f"Exit status: {result.returncode}")
        print(f"Stderr: {result.stderr}")
        return

    # Parse response time and file size from curl output
    output = result.stdout.strip()
    error_output = result.stderr.strip() if result.stderr else "No error output"

    try:
        response_time, file_size = map(float, output.split())
        # Calculate bandwidth in bytes per second
        bandwidth = file_size / response_time if response_time > 0 else 0
        print(f"URL: {url}")
        print(f"File Size: {int(file_size)} bytes")
        print(f"Response Time: {response_time:.2f} seconds")
        print(f"Bandwidth: {bandwidth / 1024:.2f} KB/s\n")
    except ValueError:
        print(f"Failed to parse output: {output}")
        print(f"Curl Error Output: {error_output}")

# Run the test for HTTP
print("Testing GOPHER bandwidth:")
test_bandwidth(HTTP_URL)

# Run the test for HTTPS
print("Testing GOPHERS bandwidth:")
test_bandwidth(HTTPS_URL, use_https=True)
