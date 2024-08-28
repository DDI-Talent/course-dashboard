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
        self.courses_file = row['courses_file']
        self.personas_file = row['personas_file']    
        self.description = row['description']            
        self.link = row['link']            
