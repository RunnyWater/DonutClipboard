import json
path = 'src/json/clipboard_data.json'
def get_clipboard_data():
    global path
    with open(path, 'r') as f:
        data = json.load(f)
        for key in list(data.keys()).copy():
            data[int(key)] = data.pop(key)
        return data
    
def set_new_bind(data):
    global path
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def load(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("The file was not found.")
        except json.JSONDecodeError:
            return {}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
def save(path):
    with open(path, 'w') as f:
        json.dump(path, f, indent=4)