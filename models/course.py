import pandas as pd
import math 
from shiny import ui, reactive
# import fontawesome as fa 
from faicons import icon_svg as icon
from views.style_service import StyleService



class Course:

    def __init__(self, row):
        self.years = self.string_to_list(f"{row['year']}")
        self.blocks = self.string_to_list(f"{row['block']}")
        self.id = row['course_id']
        self.degree_id = row['degree_id']
        self.name = row['course_name']
        self.proglang = row['Prog Lang']
        self.link = row['DRPS link']
        self.compulsory = row['Compulsory']
        self.credits = row['Credits']
        self.isprereq = row['is pre-req (ID)']
        self.hasprereq = row['has pre-req']
        self.card_colour = reactive.value("background-color: #ffffff")
    
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
        button_label = StyleService.name_shorter(self.name)
        buttons = []
        for year in self.years:
            for block in self.blocks:
                button_uid = self.to_button_id(year, block, "buttonadd_") #TODO: use course year and block in id
                buttons.append(ui.input_action_link(button_uid, 
                                f"📌 Y{year} B{block}",
                                style="background-color: #ffff00; margin: 10px;"),

                            )
        credits = f"Credits: {self.credits}"
        more_info_card = StyleService.info_card_for_course(self)
        return ui.div( 
                            ui.div(  button_label),
                            ui.div( 
                                ui.popover( icon("circle-info"), more_info_card), 
                                credits,
                                *[button for button in buttons],
                                style = "margin:0px, display:contents",
                                # proglang_footer     
                            ),
                        style= StyleService.style_course_box(),
                        hidden = (not show)
                    )


    def __repr__(self) -> str:
        return f"course id is: {self.id}, year is: {self.years}, block is: {self.blocks}, name is: {self.name}, credits: {self.credits}, colour: {self.card_colour.get()}"
    
    def string_to_list(self, string_to_parse):
        string_to_parse = string_to_parse.replace(" and ", " ").replace(" or ", " ")
        return [int(item) 
                for item in string_to_parse.split(' ')]
