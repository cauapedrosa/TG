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
        return f'{type(self).__name__}(\nCourseID={self.course_id}, \nTitle={self.title}, \nPoster={self.poster}, \nDate={self.date}, \nLocale={self.locale})'
