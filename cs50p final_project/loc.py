def count_lines(file_path):
    lines_of_code = []
    with open(file_path, encoding='utf-8') as file:
        lines = file.readlines()

        for line in lines:
            if line.strip():  # Check for non-empty lines
                if not line.lstrip().startswith("#"):  # skip lines with leading white space and #
                    lines_of_code.append(line)
        return f"You've written {len(lines_of_code)} lines of code"

# import requests
print(count_lines('project.py'))
# parameters = {
#     'date': '2024-12-01',
#     'api_key': 'Wv8R3GGi9OViHJ2LeJBughf5xhtwOePgGH1Gnem0',
# }
# NASA_URL_ENDPOINT = 'https://api.nasa.gov/planetary/apod'
# response = requests.get(NASA_URL_ENDPOINT,
#                         params=parameters
#                         )
# print(response.json())
