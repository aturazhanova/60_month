import requests

# Endpoint URL
url = 'http://127.0.0.1:5000/process-pdf'  # Make sure this matches your Flask app route

# Open the PDF file in binary mode and read its content
with open('pdf-files/short.pdf', 'rb') as file:
    # Prepare the payload
    files = {'file': file}
    
    # Send POST request to the API
    response = requests.post(url, files=files)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response as JSON
    result = response.json()
    
    # Print the boolean value
    print(result['result'])
else:
    print("Error:", response.text)
