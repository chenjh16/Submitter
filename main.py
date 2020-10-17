#!/usr/bin/env python3

###############################################################################
#
# A submitter for web learning 2018, Tsinghua University.
#
# Features:
#   1. Submit the grades, the comments, and the files.
#   2. Extract the grades from the annotations in the PDF file.
#
# Usage:
#   1. Install `PyPDF3` and `splinter` packages, and make splinter functional.
#      Firefox is recommended.
#   2. Run `main.py homework_dir`, e.g.,
#      `main.py ./离散数学\(1\)_2020-10-13\ 09_00_第四周作业/`.
#
# Notice:
#   1. The `course_id` and the `homework_id` are automatically parsed from the
#      folder name, e.g., for `离散数学(1)_2020-09-22 09_00_第一周作业`, the
#      `course_id` is `离散数学(1)` and the `homework_id` is `第一周作业`.
#   2. Note that the `homework_id` should be **fully showed** in the browser.
#   3. The `grade` is automatically parsed from the **annotations** of the PDF
#      file, e.g., `10.0` or `X.X`.
#
# Customization:
#   Override `get_tutor_info`, `get_submit_list`, `get_submit_info` methods.
#
###############################################################################

import os
import re
import sys
import PyPDF3
from submitter import Submitter


def get_tutor_info():
    """
    This method is used to collect the login information of the Web Learning 2018.
    Return an url of login page, an user name, and a password.
    :return: login_url, username, password
    """
    login_url = "http://learn.tsinghua.edu.cn"
    # For example, the user name and the password are saved in a file.
    lines = open(os.path.expanduser('~') + '/.learn.pw', 'r').readlines()
    username = lines[0].strip()
    password = lines[1].strip()
    return login_url, username, password


def get_submit_info():
    """
    This method is used to collect the information of the course ID and the homework ID.
    They can be parsed from the file name of the downloaded zip file.
    Default name of the homework folder unzipped from *.zip has the form of
    `courseId_XXXX_homeworkId`, we can just split it by '_' and the get the course ID
    and the homework ID.
    :return: course_id : string, homework_id : string
    """
    file_dir = sys.argv[1]
    identifiers = os.path.basename(file_dir).split('_')
    return identifiers[0], identifiers[-1]


def get_submit_list():
    """
    The submit list is a tuple (studentId, grade, comment, extraFile)
    and the fail list is arbitrary list.
    :return: submit_list : (4) list, fail_list : a list
    """
    submit_list = []  # a list of tuples: [(studentId, grade, comment, extraFile)]
    fail_list = []
    file_dir = os.path.abspath(sys.argv[1])
    print(file_dir)
    for item in os.listdir(file_dir):  # like: 2020010111_NAME_XXXX.pdf
        if 'Submitted' in item:  # skip submitted files.
            continue
        if 'log' in item:  # skip other file like logs.
            continue
        stu_id = item[:10]  # todo: use a robuster method.
        if stu_id.isalnum():
            exfile = os.path.join(file_dir, item)
            if os.path.splitext(item)[-1] == '.pdf':
                comment = '详见附件！'
                grade = get_grade_from_pdf_file(exfile)
                if grade == "":
                    grade = get_grade_from_filename(item)
                if grade == "":
                    fail_list.append((stu_id, grade, comment, exfile))
                else:
                    exfile = rename_file_with_grade(exfile, grade)
                    submit_list.append((stu_id, grade, comment, exfile))
            else:
                comment = '非PDF文件不予批阅，请补交PDF文件作业！'
                submit_list.append((stu_id, "0.0", comment, exfile))
    return submit_list, fail_list


def single_task_finished(task):
    print("Submitted!", task)
    file = task[-1]
    if os.path.isfile(file):
        file_dir = os.path.dirname(file)
        filename = os.path.basename(file)
        fns = filename.split('_')
        fns.insert(2, 'Submitted')
        new_file = os.path.join(file_dir, '_'.join(fns))
        os.rename(file, new_file)


def get_grade_from_pdf_file(pdf_file):
    """
    Return a grade extracted from the PDF file, such as "10.0" or "9.5".
    :param pdf_file: file_path : string
    :return: grade : string
    """
    input1 = PyPDF3.PdfFileReader(open(pdf_file, "rb"), strict=False)
    page0 = input1.getPage(0)
    if '/Annots' in page0:
        for annot in page0['/Annots']:
            annot_obj = annot.getObject()
            if '/Contents' in annot_obj:
                content = str(annot_obj['/Contents'])
                if is_grade(content):
                    return content
    return ""


def get_grade_from_filename(filename):
    """
    The file name always begin with student ID, e.g. 2015012065, 
    and then a grade, like '_9.5_', is appended to the student ID.
    """
    names = filename.split('_')
    if len(names) >= 2:
        grade = names[1]
        if is_grade(grade):
            return grade
    return ""


def rename_file_with_grade(file, grade):
    """
    Insert the grade to the PDF file name.
    :param file: a string of the PDF filename
    :param grade: a string of the grade
    :return: a string of the new filename
    """
    file_dir = os.path.dirname(file)
    filename = os.path.basename(file)
    fns = filename.split('_')
    if len(fns) >= 2 and is_grade(fns[1]):
        fns[1] = grade
    else:
        fns.insert(1, grade)
    new_file = os.path.join(file_dir, '_'.join(fns))
    os.rename(file, new_file)
    return new_file


def is_grade(num):
    """
    Judge if a string is a grade like `X.X` or `10.0`.
    :param num: a string.
    :return: True or False
    """
    return True if re.compile(r'^[0-9]\d*\.\d$').match(num) else False


def print_list(plist):
    """
    Print a list.
    :param plist: a list.
    :return: None.
    """
    for item in plist:
        print(item)


def main():
    print('Process the files in: ')
    submit_list, fail_list = get_submit_list()
    print('\nSubmit list: ' + str(len(submit_list)))
    print_list(submit_list)
    print('\nFail list: ' + str(len(fail_list)))
    print_list(fail_list)
    run = input('\nInput Y to begin submit now: ')
    if run == 'Y':
        print('\nBegin submit: ')
        url, username, password = get_tutor_info()
        course_id, homework_id = get_submit_info()
        submitter = Submitter(url, username, password, course_id, homework_id, submit_list)
        submitter.add_single_task_callback(single_task_finished)
        submitter.start()
        submitter.clean()


if __name__ == "__main__":
    main()
