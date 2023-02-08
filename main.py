import requests
import os
import tarfile
import time
import shutil
import parse_log
import stat


def download_and_extract(submission_prefix, netid, url):
    # the url is a tar.gz file, download it, create a netid folder, and extract the tar.gz file to the netid folder
    # download
    r = requests.get(url, allow_redirects=True)
    open(os.path.join('out', '{}.{}.tar.gz'.format(submission_prefix, netid)), 'wb').write(r.content)

    # extract to the netid folder
    with tarfile.open(os.path.join('out', '{}.{}.tar.gz'.format(submission_prefix, netid)), "r:gz") as tar:
        tar.extractall(os.path.join('out', submission_prefix, netid))


def download_and_extract_all_students_submissions(submission_prefix, netids, urls):
    # download url and extract to netid folder
    for netid, url in zip(netids, urls):
        # download
        download_and_extract(submission_prefix, netid, url)
        # extract
        # extract_student_submission(netid)
        pass


# https://stackoverflow.com/questions/23036576/python-compare-two-files-with-different-line-endings
def cmp_lines(path_1, path_2):
    l1 = l2 = True
    with open(path_1, 'r') as f1, open(path_2, 'r') as f2:
        while l1 and l2:
            l1 = f1.readline()
            l2 = f2.readline()
            if l1 != l2:
                return False
    return True


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


def copy_files_from_referential_to_submissions(folder_path, referential_folder_path, filtered_filenames):
    # collect all hash values of files in directory walk of referential_folder_path, and put them in a adictionary
    referential_hash_values = dict()
    for root, dirs, files in os.walk(referential_folder_path):
        for file in files:
            if file in filtered_filenames:
                continue
            file_path = os.path.join(root, file)
            # get relative file_path to referential_folder_path
            relative_file_path = os.path.relpath(file_path, referential_folder_path)

            referential_hash_values[relative_file_path] = file_path
            pass
        pass

    # check if the hash values of files in directory walk of folder_path are the same as the ones in referential_hash_values
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), stat.S_IRWXU | stat.S_IRWXG |stat.S_IRWXO)
        for file in files:
            file_path = os.path.join(root, file)
            os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG |stat.S_IRWXO)
            if file in filtered_filenames:
                continue
            relative_file_path = os.path.relpath(file_path, folder_path)
            if relative_file_path in referential_hash_values and file not in filtered_filenames:
                # copy the file from referential_hash_values to file_path
                shutil.copy(referential_hash_values[relative_file_path], file_path)
                pass
        pass


def submit_netid_submission(netid, submission_prefix):
    # print netid
    print(netid)
    # print the output of the shell command ./rai-linux-amd64
    retvalue = os.system("rai-linux-amd64 -p {} >{} 2>&1".format(os.path.join("out", submission_prefix, netid),
                                                                   os.path.join('out',
                                                                                submission_prefix + "." + netid + ".log")))
    # print error log if retvalue is not 0
    if retvalue != 0:
        print("submission failed log: {} {}".format(netid, retvalue))
        pass


# "./rai-linux-amd64 -p {}".format(os.path.join(".", submission_prefix, netid))
def submit_all_netids_submissions(netids, submission_prefix):
    for netid in netids:
        submit_netid_submission(netid, submission_prefix)
        # wait for 30 seconds
        # time.sleep(30)


def extract_netids_urls_from_csv(filename):
    import csv
    netids = []
    urls = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # netids.append(row['username'])
            # urls.append(row['projecturl'])
            if '_id' in row:
                netids.append(row['_id'])
            else:
                netids.append(row['\ufeff_id'])
            urls.append(row['purl'])
            pass
        pass
    return netids, urls


def test():
    print(calc_hash_of_file("main.py"))

    # specifications below
    submission_prefix = "scatter"
    referential_folder_path = os.path.join("gpu-algorithms-labs", "labs", submission_prefix)
    # netids, urls = extract_netids_urls_from_csv(submission_prefix + ".csv")
    netids, urls = extract_netids_urls_from_csv(os.path.join("sensitive_data", "aggregation_query.csv"))
    filtered_filenames = ["main.cu"]
    # specifications above

    download_and_extract_all_students_submissions(submission_prefix, netids, urls)
    for netid in netids:
        # compare_content_of_files(os.path.join('out',submission_prefix, netid), referential_folder_path, filtered_filenames)
        copy_files_from_referential_to_submissions(os.path.join('out', submission_prefix, netid),
                                                   referential_folder_path, filtered_filenames)
    # submit_all_netids_submissions(netids, submission_prefix)
    submit_netid_submission("cdcai2","scatter")
    parse_log.parse_log("scatter","cdcai2")

def grade_scatter():
    # specifications below
    submission_prefix = "scatter"
    referential_folder_path = os.path.join("gpu-algorithms-labs", "labs", submission_prefix)
    # netids, urls = extract_netids_urls_from_csv(submission_prefix + ".csv")
    netids, urls = extract_netids_urls_from_csv(os.path.join("sensitive_data", "scatter.csv"))
    filtered_filenames = ["main.cu"]
    # specifications above

    if 0: #already done
        download_and_extract_all_students_submissions(submission_prefix, netids, urls)
        for netid in netids:
            # compare_content_of_files(os.path.join('out',submission_prefix, netid), referential_folder_path, filtered_filenames)
            copy_files_from_referential_to_submissions(os.path.join('out', submission_prefix, netid),
                                                    referential_folder_path, filtered_filenames)
        submit_all_netids_submissions(netids, submission_prefix)
    parse_log.parse_all_logs(submission_prefix,netids)

def grade_gather():
    # specifications below
    submission_prefix = "gather"
    referential_folder_path = os.path.join("gpu-algorithms-labs", "labs", submission_prefix)
    # netids, urls = extract_netids_urls_from_csv(submission_prefix + ".csv")
    netids, urls = extract_netids_urls_from_csv(os.path.join("sensitive_data", "gather.csv"))
    filtered_filenames = ["main.cu"]
    # specifications above

    download_and_extract_all_students_submissions(submission_prefix, netids, urls)
    for netid in netids:
        # compare_content_of_files(os.path.join('out',submission_prefix, netid), referential_folder_path, filtered_filenames)
        copy_files_from_referential_to_submissions(os.path.join('out', submission_prefix, netid),
                                                   referential_folder_path, filtered_filenames)
    submit_all_netids_submissions(netids, submission_prefix)
    parse_log.parse_all_logs(submission_prefix,netids)

def grade_stencil():
    # specifications below
    submission_prefix = "stencil"
    referential_folder_path = os.path.join("gpu-algorithms-labs", "labs", submission_prefix)
    # netids, urls = extract_netids_urls_from_csv(submission_prefix + ".csv")
    netids, urls = extract_netids_urls_from_csv(os.path.join("sensitive_data", "stencil.csv"))
    filtered_filenames = ["template.cu"]
    # specifications above

    download_and_extract_all_students_submissions(submission_prefix, netids, urls)
    for netid in netids:
        # compare_content_of_files(os.path.join('out',submission_prefix, netid), referential_folder_path, filtered_filenames)
        copy_files_from_referential_to_submissions(os.path.join('out', submission_prefix, netid),
                                                   referential_folder_path, filtered_filenames)
    submit_all_netids_submissions(netids, submission_prefix)
    parse_log.parse_all_logs(submission_prefix,netids)

def parse_stencil_logs():
    submission_prefix = "stencil"
    netids, urls = extract_netids_urls_from_csv(os.path.join("sensitive_data", "stencil.csv"))
    parse_log.parse_all_logs(submission_prefix,netids)

if __name__ == '__main__':
    # sanity check: if out does not exist, then create it
    if not os.path.exists('out'):
        os.mkdir('out')
    print("now grading stencil")
    #grade_stencil()
    parse_stencil_logs()