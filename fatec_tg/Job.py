from datetime import date


class Job:

    def __init__(self, url, course_id, title, desc, date):
        self.url = url
        self.course_id = course_id
        self.title = title
        self.desc = desc
        self.date = date
