# Splinter-Submitter
A submitter for web learning 2018, Tsinghua University.

## Features:

1. Submit the grades, the comments, and the files.
2. Extract the grades from the annotations in the PDF file.

## Usage:

1. Install `PyPDF3` and `splinter` packages, and make splinter functional. Firefox is recommended.
2. Run `main.py homework_dir`, e.g., `main.py ./离散数学\(1\)_2020-10-13\ 09_00_第四周作业/`.

## Notice:

1. The `course_id` and the `homework_id` are automatically parsed from the folder name, e.g., for `离散数学(1)_2020-09-22 09_00_第一周作业`, the `course_id` is `离散数学(1)` and the `homework_id` is `第一周作业`.
2. Note that the `homework_id` should be **fully showed** in the browser.
3. The `grade` is automatically parsed from the **annotations** of the PDF file, e.g., `10.0` or `X.X`.

## Customization:

Override `get_tutor_info`, `get_submit_list`, `get_submit_info` methods.
