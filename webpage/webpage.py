# Used for storing scraped inforamtion about specific pages
# Think about it
class elementTypes:
    def integer():
        pass
    def parse_integer():
        pass
    def string():
        pass


class Webpage():
    def __init__(self) -> None:
        self.link = None
        self.raw_data = None
        self.snaphot_date = None

    def add_element(self, 
                    type:str,
                    name:str,
                    element)