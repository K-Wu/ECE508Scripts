import requests
import os
import tarfile
import time


def download_and_extract(submission_prefix, netid, url):
    # the url is a tar.gz file, download it, create a netid folder, and extract the tar.gz file to the netid folder
    import shutil
    # download
    r = requests.get(url, allow_redirects=True)
    open('{}.{}.tar.gz'.format(submission_prefix, netid), 'wb').write(r.content)

    os.mkdir(netid)
    # extract to the netid folder
    with tarfile.open('{}.{}.tar.gz'.format(submission_prefix, netid), "r:gz") as tar:
        tar.extractall(os.path.join(submission_prefix, netid))


def download_and_extract_all_students_submissions(submission_prefix, netids, urls):
    # download url and extract to netid folder
    for netid, url in zip(netids, urls):
        # download
        download_and_extract(submission_prefix, netid, url)
        # extract
        # extract_student_submission(netid)
        pass


def calc_hash_of_file(file_path):
    import hashlib
    with open(file_path, "rb") as f:
        bytes = f.read()  # read entire file as bytes
        readable_hash = hashlib.sha256(bytes).hexdigest()
        return readable_hash


# referential_folder_path is usually gpu-algorithms-labs/labs/{submission_prefix}
# and folder_path is usually {submission_prefix}/{netid}
def compare_hash_of_files(folder_path, referential_folder_path, filtered_filenames):
    # collect all hash values of files in directory walk of referential_folder_path, and put them in a adictionary
    referential_hash_values = dict()
    for root, dirs, files in os.walk(referential_folder_path):
        for file in files:
            if file in filtered_filenames:
                continue
            file_path = os.path.join(root, file)

            referential_hash_values[file] = calc_hash_of_file(file_path)
            pass
        pass

    # check if the hash values of files in directory walk of folder_path are the same as the ones in referential_hash_values
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file in filtered_filenames:
                continue
            file_path = os.path.join(root, file)
            hash_value = calc_hash_of_file(file_path)
            if hash_value != referential_hash_values[file]:
                print("hash mismatch!: {} has different hash value".format(file_path))
                pass
            pass
        pass


# "./rai-linux-amd64 -p {}".format(os.path.join(".", submission_prefix, netid))
def submit_all_netids_submissions(netids, submission_prefix):
    for netid in netids:
        # print netid
        print(netid)
        # print the output of the shell command ./rai-linux-amd64
        retvalue = os.system("./rai-linux-amd64 -p {} >{} 2>&1".format(os.path.join(".", submission_prefix, netid),
                                                                       submission_prefix + "." + netid + ".log"))
        # print error log if retvalue is not 0
        if retvalue != 0:
            print("submission failed log: {} {}".format(netids, retvalue))
            pass
        # wait for 30 seconds
        time.sleep(30)


def extract_netids_urls_from_csv(filename):
    import csv
    netids = []
    urls = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            netids.append(row['username'])
            urls.append(row['projecturl'])
            pass
        pass
    return netids, urls


if __name__ == '__main__':

    print(calc_hash_of_file("main.py"))

    # specifications below
    submission_prefix = "scatter"
    referential_folder_path = os.path.join("gpu-algorithm-labs", "labs", submission_prefix)
    netids, urls = extract_netids_urls_from_csv(submission_prefix + ".csv")
    filtered_filename = "template.cu"
    # specifications above

    download_and_extract_all_students_submissions(submission_prefix, netids, urls)
    for netid in netids:
        compare_hash_of_files(os.path.join(submission_prefix, netid), referential_folder_path, filtered_filenames)
    submit_all_netids_submissions(netids, submission_prefix)
