import urllib.request
import urllib.error
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import os, json, UnityPy, requests, urllib.request, concurrent.futures, shutil, lzma
# Function to process each URL
def process_url(i):
    a = i + 0
    url = f'https://h68.gph.netease.com/Assets/{a}/android/filelist'
    try:
        urllib.request.urlopen(url)
        response = requests.head(url)
        if response.status_code == 200:
            last_modified = response.headers.get("Last-Modified")
            if last_modified:
                print(f"{a} {last_modified}")
            else:
                print("Last-Modified header not found in the response.")
    except urllib.error.HTTPError as e:
        # Return code error (e.g. 404, 501, ...)
        # Uncomment if you want to print the error
        # print(f"HTTPError for URL {url}: {e}")
        pass
    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        # Uncomment if you want to print the error
        # print(f"URLError for URL {url}: {e}")
        pass

# Number of threads to use
max_threads = 100

# Use ThreadPoolExecutor to process URLs in parallel
with ThreadPoolExecutor(max_workers=max_threads) as executor:
    executor.map(process_url, range(8900, 9999))


version = input('\nWhich version do you want to download?')
url = f'https://h68.gph.netease.com/Assets/{version}/android/filelist'

response = requests.get(url, stream=True)

# Check if the request was successful
if response.status_code == 200:
    try:
        a = lzma.decompress(response.content[4:])
        with open("android.json", 'wb') as f_out:
            f_out.write(a)
        print(f"Downloaded, decompressed, and saved JSON file to android.json")

    except lzma.LZMAError as e:
        print(f"An error occurred during decompression: {e}")
    except json.JSONDecodeError as e:
        print(f"An error occurred while decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
def dlbundles(name, assetlist):
    bundlename = assetlist["path"]
    bundlehash = assetlist["md5"]
    save_path = f"assets/{bundlename}"
    hash_path = f"assets_hash/{bundlename}.hash"
    if os.path.exists(hash_path):
        with open(hash_path, 'r') as f:
            data = f.read()
        if data == bundlehash:
            return
    bundle = requests.get(f"{name}{bundlename}")
    if bundle.status_code == 200:
        header = bundle.content[:4]
        if header == b'RRPP':
            env = UnityPy.load(bundle.content[4:])
            for obj in env.objects:
                if obj.type.name in ["AssetBundle"]:
                    data = obj.read()
                    print(data.name)
                    save_path = "assets/" + bundlename.replace(bundlename.split("/")[-1], data.name) + ".bundle"
                    directory_path = os.path.dirname(save_path)
                    if not os.path.exists(directory_path):
                        os.makedirs(directory_path)
                    outfile = open(save_path, 'wb')
                    outfile.write(bundle.content[4:])
                    outfile.close()
                directory_path = os.path.dirname(hash_path)
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)  
                with open(hash_path, 'w') as f:
                    f.write(bundlehash)
        else:
            directory_path = os.path.dirname(save_path)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            with open(save_path, 'wb') as f:
                f.write(bundle.content)
            directory_path = os.path.dirname(hash_path)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)                
            with open(hash_path, 'w') as f:
                f.write(bundlehash)
    
with open(f'android.json', 'r', encoding = "utf8") as f:
    data = json.load(f)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(dlbundles, url.replace(f"filelist", ""), data2) for data2 in data["files"]]