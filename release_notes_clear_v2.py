# remove all releaseNotes from files in: Itegrations, Playbooks, Reports and Scripts.
# Note: using yaml will destroy the file structures so filtering as regular text-file.\
# Note2: file must be run from root directory with 4 sub-directories: Integration, Playbook, Reports, Scripts
# Usage: python release_notes_clear.py
import os
import yaml
import json
import shutil
import argparse

from Tests.scripts.validate_files import FilesValidator
from Tests.test_utils import server_version_compare, run_command, get_release_notes_file_path


def yml_remove_releaseNote_record(file_path, current_server_version, version_dir):
    """
    locate and remove release notes from a yaml file.
    :param file_path: path of the file
    :param current_server_version: current server GA version
    :return: True if file was changed, otherwise False.
    """
    with open(file_path, 'r') as f:
        yml_data = yaml.safe_load(f)

    v = yml_data.get('fromversion') or yml_data.get('fromVersion')
    if v and server_version_compare(current_server_version, str(v)) < 0:
        print('keeping release notes for ({})\nto be published on {} version release'.format(
            file_path,
            current_server_version
        ))
        return False

    rn_file = get_release_notes_file_path(file_path)
    # shutil.move(rn_file, os.path.join('Releases', version_dir, os.path.basename(rn_file)))
    run_command('git mv {} {}'.format(rn_file, os.path.join('Releases', version_dir, os.path.basename(rn_file))))
    return True


def json_remove_releaseNote_record(file_path, current_server_version, version_dir):
    """
    locate and remove release notes from a json file.
    :param file_path: path of the file
    :param current_server_version: current server GA version
    :return: True if file was changed, otherwise False.
    """
    with open(file_path, 'r') as f:
        json_data = json.load(f)

    v = json_data.get('fromversion') or json_data.get('fromVersion')
    if v and server_version_compare(current_server_version, str(v)) < 0:
        print('keeping release notes for ({})\nto be published on {} version release'.format(
            file_path,
            current_server_version
        ))
        return False

    rn_file = get_release_notes_file_path(file_path)
    # shutil.move(rn_file, os.path.join('Releases', version_dir, os.path.basename(rn_file)))
    run_command('git mv {} {}'.format(rn_file, os.path.join('Releases', version_dir, os.path.basename(rn_file))))
    return True


FILE_EXTRACTOR_DICT = {
    '.yml': yml_remove_releaseNote_record,
    '.json': json_remove_releaseNote_record,
}


def main(root_dir):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('version', help='Release version')
    arg_parser.add_argument('git_sha1', help='commit sha1 to compare changes with')
    arg_parser.add_argument('server_version', help='Server version')
    args = arg_parser.parse_args()

    # get changed yaml/json files (filter only relevant changed files)
    fv = FilesValidator()
    change_log = run_command('git diff --name-status {}'.format(args.git_sha1))
    modified_files, added_files, _, _ = fv.get_modified_files(change_log)

    version_dir = os.path.join(root_dir, 'Releases', args.version)
    try:
        os.makedirs(version_dir)
    except OSError:
        # in python 3 this could be replace with keyword argument exist_ok=True
        pass

    all_release_notes = set(os.listdir(os.path.join('Releases', 'LatestRelease')))

    for file_path in added_files.union(modified_files):
        if isinstance(file_path, tuple):
            file_path = file_path[1]

        file_extension = os.path.splitext(file_path)[1]
        FILE_EXTRACTOR_DICT[file_extension](file_path, args.server_version, args.version)

    # for file_path in added_files:
    #     file_extension = os.path.splitext(file_path)[1]
    #     FILE_EXTRACTOR_DICT[file_extension](file_path, args.server_version, args.version)


if __name__ == '__main__':
    main(os.path.dirname(__file__))
