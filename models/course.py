import pandas as pd
from shiny import ui

class Course:

    def __init__(self, row):
        self.years = self.string_to_list(row['year'])
        self.blocks = self.string_to_list(row['block'])
        self.id = row['course_id']
        self.name = row['course_name']


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

    def as_card_selected(self):
        button_label = self.name
        buttons = []
        for year in self.years:
            for block in self.blocks:
                button_uid = self.course_to_button_id(year, block) #TODO: use course year and block in id
                buttons.append(ui.input_action_button(button_uid, 
                                f"TAKEN in Y{year} B{block}")
                            )

        return ui.card(
                ui.card_header(button_label),
                *buttons,
                ui.card_footer(f"some course description here"),
                full_screen=True,
            )
    
    def __repr__(self) -> str:
        return f"course id is: {self.id}, year is: {self.years}, block is: {self.blocks}, name is: {self.name}"
    
        # turns string like "1 or 2" into ([(1, 'or') (2, 'or')]). turns "1" into [1[], and "banana" into []
    def string_to_list(self, string_to_parse):
        # "1 or 2"    "1 and 6"    "1"
        string_to_parse = string_to_parse.replace(" and ", " ").replace(" or ", " ")
        # "1 2"     "1 6"     "1"
        return [int(item) 
                for item in string_to_parse.split(' ')]

loaded_df = pd.read_csv(f'./data/example_course_outline.csv')
one_row = loaded_df.iloc[0]
print(one_row)
databases_course = Course(one_row)
print(databases_course)

print(databases_course.years)