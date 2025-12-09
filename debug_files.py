import os

print("📂 Listing all files in:", os.getcwd())
print("-" * 30)

files = os.listdir()
found_env = False

for f in files:
    print(f"📄 Found file: '{f}'")
    if ".env" in f:
        found_env = True
        if f == ".env.txt":
            print("   🚨 ERROR FOUND: Your file is named '.env.txt' (it should be just '.env')")
        elif f == ".env":
            print("   ✅ SUCCESS: Found a correctly named '.env' file.")

if not found_env:
    print("\n❌ ERROR: No .env file found at all.")