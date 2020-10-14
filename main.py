#!/usr/bin/env python3

#
# A submitter for web learning 2018, Tsinghua University
#
# Usage:
#
#   Override `get_info` and `get_submit_list` (or `get_submit_info`) methods.
#   ./submiter.py pdf_file_dir
#

import os
import re
import sys
import PyPDF3
from submitter import Submitter


def get_tutor_info():
    """
    Return url of login page, user name, and the password.
    :return: login_url, username, password
    """
    login_url = "http://learn.tsinghua.edu.cn"
    lines = open(os.path.expanduser('~') + '/.learn.pw', 'r').readlines()
    username = lines[0].strip()
    password = lines[1].strip()
    return login_url, username, password


def get_submit_list():
    """
    The submit list is a tuple (studentId, grade, comment, extraFile)
    and the fail list is arbitrary list.
    :return: submit_list : (4) list, fail_list : a list
    """
    submit_list = []
    fail_list = []
    file_dir = os.path.abspath(sys.argv[1])
    print(file_dir)
    for item in os.listdir(file_dir):
        if 'Submitted' in item:
            continue
        if 'log' in item:
            continue
        stu_id = item[:10]
        if stu_id.isalnum():
            exfile = file_dir + '/' + item
            if os.path.splitext(item)[1] == '.pdf':
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


def get_submit_info():
    """
    Default homework folder unzip from *.zip has the form `courseId_XXXX_homeworkId`,
    we can just split it by '_'.
    :return: course_id : string, homework_id : string
    """
    file_dir = sys.argv[1]
    identifiers = os.path.basename(file_dir).split('_')
    return identifiers[0], identifiers[-1]


def single_task_callback(list):
    print("Submitted!", list)
    file = list[-1]
    if os.path.isfile(file):
        filedir = os.path.dirname(file)
        filename = os.path.basename(file)
        fns = filename.split('_')
        fns.insert(2, 'Submitted')
        new_file = os.path.join(filedir, '_'.join(fns))
        os.rename(file, new_file)


def get_grade_from_pdf_file(pdf_file):
    """
    Return a grade extracted from the PDF file, such as "9.5".
    :param pdf_file: file_path : string
    :return: grade : string,
    """
    try:
        input1 = PyPDF3.PdfFileReader(open(pdf_file, "rb"), strict=False)
        page0 = input1.getPage(0)
        for annot in page0['/Annots']:
            try:
                content = str(annot.getObject()['/Contents'])
                if is_grade(content):
                    return content
            except:
                pass
    except:
        pass
    return ""


def get_grade_from_filename(filename):
    """
    The file name always begin with student ID, s.t. 2015012065, 
    and then we should append a grade, like '_9.5_', to the student ID.
    """
    names = filename.split('_')
    grade = ""
    if len(names) >= 2:
        grade = names[1]
    if is_grade(grade):
        return grade
    return ""


def rename_file_with_grade(file, grade):
    filedir = os.path.dirname(file)
    filename = os.path.basename(file)
    fns = filename.split('_')
    if len(fns) >= 2 and is_grade(fns[1]):
        fns[1] = grade
    else:
        fns.insert(1, grade)
    new_file = os.path.join(filedir, '_'.join(fns))
    os.rename(file, new_file)
    return new_file


def is_grade(num):
    pattern = re.compile(r'^[0-9]\d*\.\d$')
    result = pattern.match(num)
    if result:
        return True
    else:
        return False


def print_list(plist):
    for item in plist:
        print(item)


def main():
    print('Process the files ...')
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
        submitter.add_single_task_callback(single_task_callback)
        submitter.start()
        submitter.clean()


if __name__ == "__main__":
    main()


