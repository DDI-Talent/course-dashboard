import pandas as pd
import math 
from shiny import ui, reactive
# import fontawesome as fa 
from faicons import icon_svg as icon



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
        self.card_colour = reactive.value("background-color: #ffffff")
    
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
                                f"📌 Y{year} B{block}",
                                style="background-color: #579a9f6d"),

                            )
        credits = f"Credits: {self.credits}"
        proglang_footer=[]
        if not pd.isna(self.proglang):
            if self.proglang == "Python":
                # footer_items.append("Programming language: ")
                proglang_footer.append(icon("python"))
                proglang = f"Programming language: Python"
            if self.proglang == "R":
                # footer_items.append("Programming language: ")
                proglang_footer.append(icon("r"))
                proglang = f"Programming language: R"
            if self.proglang == "R and SQL":
                # footer_items.append("Programming language: ")
                proglang_footer.append(icon("python"))
                proglang_footer.append("+ SQL")
                proglang = f"Programming language: Python and SQL"
        else:
            proglang = "This is not a programming course"

        
        if self.compulsory == True:
            compulsory = "This course is compulsory"
        else:
            compulsory = "This course is optional"
        if not pd.isna(self.isprereq):
            isprereq = f"This course is a prerequisite for {self.isprereq}"
        else:
            isprereq = "This course is not a prerequisite for any courses"
        if not pd.isna(self.hasprereq):
            hasprereq = f"This course has prerequisites: {self.hasprereq}"
        else:
            hasprereq = "This course does not have any prerequsites"
        
        more_info_card = (ui.card(
                                ui.row(ui.div(
                                    {"style": "font-weight: bold"},
                                    ui.p("Course Information"),
                                ),),
                                ui.row("‣ ",compulsory),
                                ui.row("‣ ",hasprereq),
                                ui.row("‣ ",isprereq),
                                ui.row("‣ ",credits),
                                ui.row("‣ ",proglang),
                                ui.row(ui.tags.a("View this course on DRPS", href=self.link, target="_blank"))
                            ))
        if len(proglang_footer) > 1:
            footer_cols = [7,5]
        else:
            footer_cols = [10,2]

        # card_color=f"background-color: #ffffff"
        # grey = #c3c3c3, white = #ffffff
        return ui.card(
                    ui.card_header((ui.row(
                            ui.column(10, button_label),
                            ui.column(2, ui.popover(
                                    icon("circle-info"), 
                                    more_info_card,
                    )))),
                    style=self.card_colour.get()),
                                    
                    ui.row(*[ui.column(int(12 / len(buttons)), button) for button in buttons]),
                    ui.card_footer(ui.row(
                            ui.column(footer_cols[0], credits),
                            ui.column(footer_cols[1], proglang_footer)), 
                            style=self.card_colour.get()),  
                    style=self.card_colour.get()
                    # full_screen=True,
                )



    def __repr__(self) -> str:
        return f"course id is: {self.id}, year is: {self.years}, block is: {self.blocks}, name is: {self.name}, credits: {self.credits}, colour: {self.card_colour.get()}"
    
        # turns string like "1 or 2" into ([(1, 'or') (2, 'or')]). turns "1" into [1[], and "banana" into []
    def string_to_list(self, string_to_parse):
        # "1 or 2"    "1 and 6"    "1"
        string_to_parse = string_to_parse.replace(" and ", " ").replace(" or ", " ")
        # "1 2"     "1 6"     "1"
        return [int(item) 
                for item in string_to_parse.split(' ')]
