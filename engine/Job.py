from datetime import date


class Job:

    def __init__(self, url, course_id, title, desc, poster, date, locale):
        self.url = url
        self.course_id = course_id
        self.title = title
        self.desc = desc
        self.poster = poster
        self.date = date
        self.locale = locale
        if(locale == None):
            self.locale = "Brasil"

    def __repr__(self) -> str:
        return f'\n{type(self).__name__}(CourseID={self.course_id}, \n    Title={self.title}, \n    Poster={self.poster}, \n    Date={self.date}, \n    Locale={self.locale})'
