import requests
from bs4 import BeautifulSoup

def list_files(url):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        
        # Parse the HTML to extract file links
        soup = BeautifulSoup(response.text, 'html.parser')
        files = [a.text for a in soup.find_all('a')]
        
        print("Available files:")
        for idx, file in enumerate(files, start=1):
            print(f"{idx}. {file}")
        
        return files
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching file list: {e}")
        return []

def download_file(url, output_path):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()

        with open(output_path, 'wb') as file:
            file.write(response.content)
        
        print(f"File downloaded successfully: {output_path}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the file: {e}")

# Server URL for listing and downloading files
server_url = 'https://localhost:8443'
files = list_files(server_url)

if files:
    # Prompt the user to select a file
    choice = int(input("Enter the number of the file to download: ")) - 1
    if 0 <= choice < len(files):
        selected_file = files[choice]
        file_url = f"{server_url}/download/{selected_file}"
        download_file(file_url, "downloaded/"+selected_file)
    else:
        print("Invalid selection.")
