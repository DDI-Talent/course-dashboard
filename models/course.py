import pandas as pd
import math 
from shiny import ui

class Course:

    def __init__(self, row):
        self.years = self.string_to_list(row['year'])
        self.blocks = self.string_to_list(row['block'])
        self.id = row['course_id']
        self.name = row['course_name']
        self.proglang = row['Prog Lang']
        self.link = row['DRPS link']
        self.compulsory = row['Compulsory']
        self.credits = row['Credits']
        self.isprereq = row['is pre-req (ID)']
        self.hasprereq = row['has pre-req']


    def takeable_in(self, year, block):
        takeable = year in self.years and block in self.blocks
        return takeable

    def to_button_id(self, year, block, action):
        return f"{action}{self.id}_{year}_{block}"
    
    def all_possible_button_ids(self):
        return [
            self.to_button_id(year, block, action)
            for year in self.years
            for block in self.blocks
            for action in ["buttonadd_", "buttonremove_"]
        ]
       

    def as_card(self):
        button_label = self.name
        buttons = []
        for year in self.years:
            for block in self.blocks:
                button_uid = self.to_button_id(year, block, "buttonadd_") #TODO: use course year and block in id
                buttons.append(ui.input_action_button(button_uid, 
                                f"TAKE in Y{year} B{block}")
                            )
        footer_items = [f"Credits: {self.credits}"]
        if not pd.isna(self.proglang):
            footer_items.append(f", Programming language: {self.proglang}")
        if self.compulsory == True:
            compulsory = "COMPULSORY\n"
        else:
            compulsory = ""
        if not pd.isna(self.isprereq):
            isprereq = f"Prerequisite for {self.isprereq}\n"
        else:
            isprereq = ""
        if not pd.isna(self.hasprereq):
            hasprereq = f"Prerequisites: {self.hasprereq}\n"
        else:
            hasprereq = ""

        return ui.card(
                    ui.card_header(button_label),
                    *buttons,
                    compulsory,
                    hasprereq,
                    isprereq,
                    ui.tags.a("DRPS link", href=self.link, target="_blank"),
                    ui.card_footer(footer_items),
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
