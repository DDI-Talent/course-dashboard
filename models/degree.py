import pandas as pd
import math 
from shiny import ui, reactive
# import fontawesome as fa 
from faicons import icon_svg as icon
from views.style_service import StyleService



class Degree:

    def __init__(self, row):
        self.id = row['id']
        self.name = row['name']   
        self.years = int(row['years'])   
        self.description = row['description']            
        self.link = row['link']            
        self.link_to_ms_form = row['link_to_ms_form']            
        self.compulsory_courses = self.string_to_list(row['compulsory_courses'], as_ints=False)

    # could this be in the deta service?
    def string_to_list(self, string_to_parse, as_ints = True):
        string_to_parse = string_to_parse.replace(" and ", " ").replace(" or ", " ").replace("+", " ")
        return [int(item) if as_ints else item
                for item in string_to_parse.split(' ')
                if item != '' and item != 'nan']
