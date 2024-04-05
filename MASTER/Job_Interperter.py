import sys
import os
import uuid
import random
import string

import string
import random
import uuid

def generate_random_string(length):
    characters = string.ascii_letters + string.digits

    random_string = ''.join(random.choice(characters) for _ in range(length))

    return random_string

def generate_unique_random_string():
    unique_id = str(uuid.uuid4()).replace('-', '')[:8]

    random_string = generate_random_string(11)

    unique_random_string = unique_id + random_string

    return unique_random_string


full_path = " ".join(sys.argv[1:])

folder_name = full_path.split("\\")[-1]

dir_path = os.path.dirname(full_path)

os.chdir(dir_path)

os.makedirs("JOB_READY_TO_RUN", exist_ok=True)

if os.path.exists("JOB_READY_TO_RUN"):
    os.chdir("JOB_READY_TO_RUN")
    file_name = generate_unique_random_string() + ".txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(folder_name)
        