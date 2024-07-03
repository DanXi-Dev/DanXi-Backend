import json

import toml

print(">>>> BEGIN: Convert toml to json >>>>")

try:
    with open("./public/tmp_wait_for_json_editor.toml", "r", encoding="utf8") as f_toml:
        with open("./public/swift.json", "w", encoding="utf8") as f_json:
            json.dump(toml.load(f_toml), f_json, ensure_ascii=False)
    print("SUCCESS")
except Exception as e:
    print("ERROR")
    raise from e

print("<<<< END: Convert toml to json <<<<")
