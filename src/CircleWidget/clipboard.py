import json, os
path = 'src/json/clipboard_data.json'

def get_clipboard_data():
    global path
    check_path(path)
    
    data = load(path)
    for key in list(data.keys()).copy():
        data[int(key)] = data.pop(key)
    return data

    
def set_new_bind(bind, value):
    global path
    data = get_clipboard_data()
    data[bind] = value
    save(path, data)

def reset_bindings(path):
    data = {
    1: "Bind it...",
    2: "Bind it...",
    3: "Bind it...",
    4: "Bind it...",
    5: "Bind it...",
    6: "Bind it...",
    7: "Bind it...",
    8: "Bind it..."
}
    save(path, data)

def load(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("The file was not found.")
        except json.JSONDecodeError:
            print("Invalid JSON data in the file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
def save(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def check_path(path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        reset_bindings(path)