import json
from urllib import request
from pathlib import Path
import zipfile, os
def main():
    print("Fetching new download URL from GitHub")
    # Getting the new release URL from GitHub REST API
    githubResponse = request.urlopen("https://api.github.com/repos/hisprofile/TF2-Trifecta/releases")
    gitData = githubResponse.read()
    # Decoding the urllib contents to JSON format
    encode = githubResponse.info().get_content_charset('utf-8')
    data = json.loads(gitData.decode(encode))
    newRelease = dict(data[0]).get("assets")
    assetsData = dict(newRelease[0])
            
    # Applying the latest download url  
    URL = assetsData.get("browser_download_url")
    filePath = Path("temp/Update.zip").parent
    newFile = Path("temp/Modifed.zip").parent
    files = [filePath, newFile]
    print("Downloading new file")
    request.urlretrieve(URL, filePath)
    print("Opening and preparing zip files")
    # Preparing to delete "addonUpdater.py" from the new zip file.
    zin = zipfile.ZipFile (filePath, 'r')
    zout = zipfile.ZipFile (newFile, 'w')

    print("Modifying the zip file for extraction")
    # Going through each file and compare the filenames to "TF2-Trifecta/addon-updater.py"
    # If the filename = to "TF2-Trifecta/addon-updater.py" it won't add the file to the new zip file
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if (item.filename != 'TF2-Trifecta/addon-updater.py'):
            zout.writestr(item, buffer)
    zout.close()
    zin.close()
    # Extracting the new zip file that dose not have to "addon-updater.py" file.
    print("Extracting the new update")
    with zipfile.ZipFile(newFile, "r") as zip_ref:
        zip_ref.extractall(path="C:\\Program Files\\Blender Foundation\\Blender 3.3\\3.3\scripts\\addons")
    # Deleting the new zipfiles to be ready for new ones and preserve disk space.
    print("Deleting zipFiles")
    for file in files:
        print(f"Deleting {file}")
        os.remove(file)
