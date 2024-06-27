class Course:

    def __init__(self, id: str, year: int, block: int, name = ""):
        self.id = id
        self.year = year 
        self.block = block
        self.name = name
    
    def as_button(self, action = "buttonadd_"):
        return f"{action}{self.id}_{self.year}_{self.block}"