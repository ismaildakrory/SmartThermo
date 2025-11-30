import hashlib, os, json, datetime, re, shutil

# pyright: reportUndefinedVariable=false
Import("env")

HEADER_PATH = "src/ui/system_state.h"
JSON_PATH = "firmware.json"

def get_fw_version(header_path="src/ui/system_state.h"):
    with open(header_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    match = re.search(r'#define\s+FW_VERSION\s+"(.+)"', content)
    if not match:
        raise ValueError("FW_VERSION not found in system_state.h")
    return match.group(1)

def get_previous_version(json_path=JSON_PATH):
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            return data.get("version", "0.0.0")
        except Exception:
            return "0.0.0"
    else:
        return "0.0.0"

def generate_firmware_json(source, target, env):
    firmware_path = target[0].get_abspath()

    size = os.path.getsize(firmware_path)
    with open(firmware_path, "rb") as f:
        md5 = hashlib.md5(f.read()).hexdigest()

    release_date = datetime.date.today().isoformat()
    version = get_fw_version()
    min_version = get_previous_version()

    # Construct the specific filename based on version
    new_bin_name = f"firmware_v{version}.bin"
    url = f"http://api.ismaildakrory.com/{new_bin_name}"

    firmware_info = {
        "version": version,
        "min_version": min_version,
        "url": url,
        "size": size,
        "md5": md5,
        "changelog": "Bug fixes and improvements",
        "release_date": release_date,
        "mandatory": False,
        "beta": False
    }

    # 1. Write the JSON file
    with open(JSON_PATH, "w") as f:
        json.dump(firmware_info, f, indent=2)

    # 2. Copy and rename the firmware binary to the project root (same dir as JSON)
    destination_path = os.path.join(os.getcwd(), new_bin_name)
    shutil.copyfile(firmware_path, destination_path)

    print(f"✅ firmware.json generated (version={version}, min_version={min_version})")
    print(f"✅ Firmware binary copied to: {destination_path}")

env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", generate_firmware_json)