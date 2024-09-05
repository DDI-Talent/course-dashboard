import pandas as pd
import math 
from shiny import ui, reactive
# import fontawesome as fa 
from faicons import icon_svg as icon
from views.style_service import StyleService



class Course:

    def __init__(self, row):
        self.degree_ids = self.string_to_list(f"{row['degree_ids']}", as_ints=False)
        self.years = self.string_to_list(f"{row['year']}")
        self.blocks = self.string_to_list(f"{row['block']}")
        self.id = row['course_id']
        self.name = row['course_name']
        self.prog_lang = self.string_to_list(f"{row['prog_lang']}", as_ints=False)
        self.notes = row['notes']
        self.has_pre_req_id = row['has_pre_req_id']
        self.link = row['drps_link']
        self.credits = row['credits']
        self.themes = self.string_to_list(f"{row['themes']}", as_ints=False)
        if "code" in self.themes:
            self.themes.remove("code")
            self.themes.extend([f"code-{language.lower()}" for language in self.prog_lang])

    
    def takeable_in(self, year, block):
        takeable = year in self.years and block in self.blocks
        return takeable
    
    def takeable_in_any(self, years, blocks):
        for year in years:
            for block in blocks:
                if self.takeable_in(year, block):
                    return True
        return False

    def to_button_id(self, year, block, action):
        return f"{action}{self.id}_{year}_{block}"
    
    def all_possible_button_ids(self):
        return [
            self.to_button_id(year, block, action)
            for year in self.years
            for block in self.blocks
            for action in ["buttonadd_", "buttonremove_"]
        ]
       

    def as_card(self, show):
        buttons = []
        for year in self.years:
            for block in self.blocks:
                button_uid = self.to_button_id(year, block, "buttonadd_")
                buttons.append(ui.input_action_link(button_uid, 
                                f"📌 Y{year} B{block}",
                                style=StyleService.style_highlighted_link()),
                            )
        return StyleService.course_as_card(self, show, buttons = buttons)
        


    def __repr__(self) -> str:
        return f"course id is: {self.id}, year is: {self.years}, block is: {self.blocks}, name is: {self.name}, credits: {self.credits}"
    
    def string_to_list(self, string_to_parse, as_ints = True):
        string_to_parse = string_to_parse.replace(" and ", " ").replace(" or ", " ").replace("+", " ")
        return [int(item) if as_ints else item
                for item in string_to_parse.split(' ')
                if item != '' and item != 'nan']
