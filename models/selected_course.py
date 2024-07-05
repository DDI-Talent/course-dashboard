import pandas as pd
from shiny import ui
from models.course import Course

class SelectedCourse:

    def __init__(self, course_info, year, block):
        self.course_info = course_info
        self.year = year
        self.block = block

    def to_selected_button_id(self, action):
        return f"{action}{self.course_info.id}_{self.year}_{self.block}"
    
    def as_card_selected(self, show = False):
        button_label = self.course_info.name
        buttons = []
        button_uid_remove = self.to_selected_button_id( "buttonremove_")
        return ui.card(
                ui.card_header(button_label + "banana"),
                ui.input_action_button(button_uid_remove, 
                                f"REMOVE"),
                ui.card_footer(f"some course description here"),
                full_screen=True,
                hidden = (not show)
            )

    def as_string(self):
        course_info = f"Course Info: {self.course_info}, Year: {self.year}, Block: {self.block}"
        return course_info   

    def __str__(self):
        return self.as_string()
    
