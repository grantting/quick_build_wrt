import os

if __name__ == "__main__":
    firmware_version = os.getenv('FIRMWARE_VERSION', 'Unknown')
    target_platform = os.getenv('TARGET_PLATFORM', 'Unknown')

    print(f"Firmware Version: {firmware_version}")
    print(f"Target Platform: {target_platform}")