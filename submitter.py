
from splinter import Browser


class Submitter:

    def __init__(self, url, username, password, course_id, homework_id, submit_list):
        self._callback = None
        self._browser = Browser()
        self._url = url
        self._username = username
        self._password = password
        self._course_id = course_id
        self._homework_id = homework_id
        self._submit_list = submit_list

    def _login(self):
        self._browser.visit(self._url)
        self._browser.fill("i_user", self._username)
        self._browser.fill("i_pass", self._password)
        self._browser.find_by_id("loginButtonId").click()

    def _nvi2course(self):
        self._browser.find_link_by_partial_text(self._course_id).first.click()
        self._browser.windows.current.close()

    def _nvi2homework(self):
        self._browser.find_link_by_partial_text("课程作业").first.click()
        self._browser.find_link_by_partial_text(self._homework_id).first.click()

    def _submit(self, stu_id, grade, comment, ex_file):
        xpath_str = '//tbody/tr[td[3]=' + stu_id + ']/td[last()]/a'
        self._browser.find_by_xpath(xpath_str).last.click()
        self._browser.fill('cj', grade)
        self._browser.fill('pynr', comment)
        if ex_file != "":
            self._browser.driver.find_element_by_name('fileupload').send_keys(ex_file)
        submit_btn_css = 'div[class="sub-back sub-back-3 absolute"] > input[class="btn"]'
        self._browser.find_by_css(submit_btn_css).first.click()
        self._browser.find_by_text('关闭').click()
        self._browser.back()
        self._browser.back()

    def add_single_task_callback(self, callback):
        self._callback = callback

    def start(self):
        self._login()
        self._nvi2course()
        self._nvi2homework()
        for stu_id, grade, comment, ex_file in self._submit_list:
            self._submit(stu_id, grade, comment, ex_file)
            self._callback([stu_id, grade, comment, ex_file])
        self._browser.quit()
