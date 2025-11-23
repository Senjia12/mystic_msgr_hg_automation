# JSON feature : loading 'dynamically' the template and blocks to follow game progress

import json

msg_nb = 5  # to know the "blocks group" to compare

def get_blocks_and_template(msg_nb, json_path='templates/templates.json'):
    with open(json_path, 'r') as f:
        data = json.load(f)

    msg_data = data.get(str(msg_nb))
    if not msg_data:
        raise ValueError(f"msg_nb {msg_nb} not found in JSON file.")

    print(f"Blocks for the message {msg_nb} : {msg_data['blocks']}")
    print(f"Template for the message {msg_nb} : {msg_data['template']}")
    return msg_data["blocks"], msg_data["template"]
    
get_blocks_and_template(msg_nb)