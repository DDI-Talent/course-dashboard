import pandas as pd
from shiny import ui
from models.course import Course
from faicons import icon_svg as icon
from views.style_service import StyleService

class CourseSelected:

    def __init__(self, course_info, year, block):
        self.course_info = course_info
        self.year = year
        self.block = block

    def to_selected_button_id(self, action):
        return f"{action}{self.course_info.id}_{self.year}_{self.block}"

    def get_credits(self):
        return self.course_info.credits
    
    def get_colour(self):
        return self.course_info.card_colour.get()

    def as_card_nothing_selected( year, block, show = False):
            button_label = "Nothing selected yet"
            
            return ui.div( 
                                ui.row( 
                                          ui.input_action_link(f"buttonfilter_{year}_{block}", f"🔎 filter course options"),
                                    style = "margin:0px"
                                ),
                                hidden = (not show)
                        ).add_class("course-box-not-selected")




    def as_card_selected(self, show = True, dissertation = False):
        button_uid_remove = self.to_selected_button_id( "buttonremove_")
        buttons = [ui.input_action_link(button_uid_remove, f"❌").add_class("highlighted-link")]
        return StyleService.course_as_card(self.course_info,show,dissertation=dissertation, buttons = buttons)

    def as_string(self):
        course_info = f"Course Info: {self.course_info}, Year: {self.year}, Block: {self.block}"
        return course_info   

    def __str__(self):
        return self.as_string()
    
