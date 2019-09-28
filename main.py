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
    file_dir = sys.argv[1]
    for item in os.listdir(file_dir):
        stu_id = item[:10]
        if stu_id.isalnum():
            grade = "0.0"
            exfile = ""
            comment = '非PDF文件不予批阅，请补交PDF文件作业！'
            if os.path.splitext(item)[1] == '.pdf':
                exfile = file_dir + '/' + item
                comment = '详见附件！'
                grade = get_grade_from_pdf_file(exfile)
            if grade == "":
                fail_list.append((stu_id, grade, comment, exfile))
            else:
                submit_list.append((stu_id, grade, comment, exfile))
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
    print('\nSubmit list: ')
    print_list(submit_list)
    print('\nFail list: ')
    print_list(fail_list)
    run = input('\nInput Y to begin submit now: ')
    if run == 'Y':
        print('\nBegin submit: ')
        url, username, password = get_tutor_info()
        course_id, homework_id = get_submit_info()
        submitter = Submitter(url, username, password, course_id, homework_id, submit_list)
        submitter.start()


if __name__ == "__main__":
    main()


