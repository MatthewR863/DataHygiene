import time
import os
import hashlib
from difflib import SequenceMatcher


class FileOrganizer:
    # attributes path, filetype,
    def __init__(self, path, folders, files, logs):
        self.path = path
        self.folders = folders
        self.files = files
        self.logs = logs

    def scandir(self):
        # scan directory for all files and folders and return a list of them
        for root, dirs, files in os.walk(self.path):
            for file in files:
                self.files.append(file)
            for folder in dirs:
                self.folders.append(folder)
        return self.files, self.folders

    def sortfilebyname(self, path):
        # sort files into folders based on their names
        alldirs = []
        for root, dirs, files in os.walk(path):
            alldirs.append((root, files))

        filenames = [f for _, files in alldirs for f in files]
        similars = {}
        threshold = 0.75
        used = set()
        group_id = 1

        for i in range(len(filenames)):
            if self.files[i] in used:
                continue

            current_group = [filenames[i]]
            used.add(filenames[i])

            for j in range(i + 1, len(filenames)):
                if filenames[j] in used:
                    continue

                similarity = SequenceMatcher(None, filenames[i], filenames[j]).ratio()

                if similarity >= threshold:
                    current_group.append(filenames[j])
                    used.add(filenames[j])

            if len(current_group) > 1:
                similars[group_id] = current_group
                group_id += 1

        def commoncore(files):
            core = files[0]
            for c in files[1:]:
                matcher = SequenceMatcher(None, core, c)
                blocks = matcher.get_matching_blocks()
                common = ''.join(core[block.a:block.a + block.size] for block in blocks if block.size > 0)
                return common

        def grpfiles(root, files):
            foldername = commoncore(files).strip("._- ")[:-15]
            folderpath = os.path.join(root, foldername)

            for i in range(len(files)):
                if os.path.isdir(folderpath):
                    try:
                        os.rename(os.path.join(root, files[i]), os.path.join(folderpath, files[i]))
                    except FileExistsError:
                        counter = 1
                        name, ext = os.path.splitext(files[i])
                        while True:
                            numbered_name = f"{name}_{counter}{ext}"
                            numbered_path = f"{folderpath}\\{numbered_name}"
                            print(numbered_path)
                            if not os.path.exists(numbered_path):
                                os.rename(os.path.join(root, files[i]), numbered_path)
                                break
                            counter += 1
                    continue
                else:
                    os.makedirs(folderpath, exist_ok=True)
                    old = os.path.join(root, files[i])
                    new = os.path.join(folderpath, files[i])
                    os.rename(old, new)

        try:
            for i, vals in similars.items():
                for root, files in alldirs:
                    grpfiles(root, vals)
        except FileNotFoundError:
            pass
            print("ERROR")

    def sortfilebytype(self, path):
        # sort files into folders based on their file type
        for root, dirs, files in os.walk(path):
            for file in files:
                name, ext = os.path.splitext(file)

                # if file is in a subfolder, sort the subfolder
                if ext[1:] not in root.split("\\")[-1]:
                    print(root.split("\\")[-1], "GGGGGGGG", ext[1:])
                    print("QQQQQQQQQQQQQQQQQQQQQQ")
                    subdir = f"{root}\\{ext[1:]}"
                    try:
                        os.mkdir(subdir)
                    except FileExistsError:
                        print("SUBDIIR", subdir)
                        self.sortfilebytype(subdir)

                # if file is not in a subfolder, sort the file
                print(self.folders)
                if root.split("\\")[-1] != ext[1:]:
                    print(root, " AAAAAAAAA ", self.folders)
                    dirname = ext[1:]
                    try:
                        os.mkdir(f"{root}\\{dirname}")  # create folder for file type if it doesn't exist
                        os.rename(f"{root}\\{file}", f"{root}\\{dirname}\\{file}")
                    except FileExistsError:
                        try:
                            os.rename(f"{root}\\{file}", f"{root}\\{dirname}\\{file}")
                            file = f"\\{dirname}\\{file}"
                        except FileNotFoundError:
                            pass

    def namefile(self):
        # rename file following naming standards (date, name, etc.)
        for file in self.files:
            if os.path.isfile(f"{self.path}\\{file}"):
                name, ext = os.path.splitext(file)
                if " " in name:
                    name = name.replace(" ", "_")
                    name = name.lower()
                timestamp = os.path.getctime(f"{self.path}\\{file}")
                timestamp = time.ctime(timestamp)
                timestamp = time.strptime(timestamp)
                timestamp = time.strftime("%Y-%m-%d", timestamp)
                if timestamp not in name:
                    name = f"{name}_{timestamp}"
                try:
                    os.rename(f"{self.path}\\{file}", f"{self.path}\\{name}{ext}")
                # file with same name already exists, add a number to the end of the file name
                except FileExistsError:
                    counter = 1
                    while True:
                        numbered_name = f"{name}_{counter}{ext}"
                        numbered_path = f"{self.path}\\{numbered_name}"
                        if not os.path.exists(numbered_path):
                            os.rename(f"{self.path}\\{file}", numbered_path)
                            break
                        counter += 1

    # implement ai to help with naming standards

    def detectduplicates(self):
        # detect duplicate files and prompt user to delete them
        duplicates = {}
        filehashes = []

        for file in self.files:
            file_path = f"{self.path}/{file}"
            hashfunction = hashlib.new("sha256")
            with open(file_path, 'rb') as f:
                contents = f.read()
                hashfunction.update(contents)
                filehashes.append(hashfunction.hexdigest())

        # duplicate found
        hash_groups = {}
        for idx, h in enumerate(filehashes):
            if h not in hash_groups:
                hash_groups[h] = []
            hash_groups[h].append(self.files[idx])

        group_id = 1
        for files in hash_groups.values():
            if len(files) > 1:
                duplicates[group_id] = files
                group_id += 1

        print(duplicates)
        return duplicates

    def deleteemptyfolders(self):
        # delete empty folders
        for folder in self.folders:
            folder_path = f"{self.path}\\{folder}"
            if os.path.isdir(folder_path) and not os.listdir(folder_path):
                os.rmdir(folder_path)

    def deleteemptyfiles(self):
        # delete empty files
        for file in self.files:
            file_path = f"{self.path}/{file}"
            if os.path.isfile(file_path) and os.path.getsize(file_path) == 0:
                os.remove(file_path)


def main():
    # test the file organizer namefile function
    path = r"C:\Users\jonat\OneDrive\Desktop\testfolder"
    folders = []
    files = []
    logs = []
    organizer = FileOrganizer(path, folders, files, logs)
    files, folders = organizer.scandir()
    organizer.sortfilebytype(path)
    organizer.sortfilebyname(path)
    organizer.namefile()


main()