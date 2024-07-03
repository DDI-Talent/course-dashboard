import pandas as pd
from shiny import ui
from models.course import Course

class SelectedCourse:

    def __init__(self, course_info, year, block):
        self.course_info = course_info
        self.year = year
        self.block = block


    def course_to_button_id(self, year, block, action = "buttonadd_"):
        return f"{action}{self.id}_{year}_{block}"
    
    def all_possible_button_ids(self):
        return [
            self.course_to_button_id(year, block)
            for year in self.years
            for block in self.blocks
        ]
       

    def as_card(self):
        button_label = self.name
        buttons = []
        for year in self.years:
            for block in self.blocks:
                button_uid = self.course_to_button_id(year, block) #TODO: use course year and block in id
                buttons.append(ui.input_action_button(button_uid, 
                                f"TAKE in Y{year} B{block}")
                            )

        return ui.card(
                ui.card_header(button_label),
                *buttons,
                ui.card_footer(f"some course description here"),
                full_screen=True,
            )
    

    def __str__(self):
        course_info = f"Course Info: {self.course_info}, Year: {self.year}, Block: {self.block}"
        return course_info
    
