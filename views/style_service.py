from shiny import  ui
import pandas as pd
from faicons import icon_svg as icon

class StyleService:
    themes = []
    def __init__(self):
        pass

    def style_theme_box(number_of_items = 1):
        item_width = 24
        max_in_row = 4
        if number_of_items > max_in_row:
            number_of_items = max_in_row
        return f"display:flex;  flex-wrap: wrap-reverse; width: {item_width*number_of_items}px;"

    def style_theme_single(theme_id):
        theme = StyleService.get_theme(theme_id)
        return f"padding:1px; text-align:center; vertical-align: middle; color:{theme.textcolor};background-color:{theme.color};"


    def get_themes():
        # load once on first use. No easier way without proper singletons.
        if len(StyleService.themes) == 0:
            import models.data_service # import here to avoid circular dependancy
            StyleService.themes = models.data_service.DataService.load_themes()
        return StyleService.themes
        
    def get_theme(theme_id):
        return [theme
         for theme in StyleService.get_themes()
          if theme.id == theme_id][0]
   
    def single_theme(theme_id, how_many_vertical, text=None):
        if text == None:
            css_class = "theme-single-size"
        else:
            css_class = "theme-single-size-with-count"

        text = text if text  else f"{StyleService.get_theme(theme_id).emoji}"
        return  ui.div(text, 
                      style = StyleService.style_theme_single(theme_id)
                      ).add_class(css_class),
    
    def box_of_course_metainfo(course_info, no_popover = False):
        more_info_card = StyleService.info_card_for_course(course_info) if not no_popover else None
        return ui.popover( 
            ui.div(
                ui.div( 
                    ui.div(
                        icon("circle-info"),
                        # ui.div(f"{course_info.credits} cred"),
                          style="right: 0px; top: 0px; position: absolute;"),
                     ),
                StyleService.box_of_themes(course_info.themes, "meta-box-half-bottom")
            ).add_class("meta-info-box"), 
            more_info_card 
        )
        

    def one_theme(theme_id, count):
        theme = StyleService.get_theme(theme_id)
        return ui.div( 
            f"{count} : {theme.emoji} {theme.name}",
            # f"{theme['description']}",
            style=f"background-color:{theme.color}; color:{theme.textcolor};padding: 0px 8px;",
        )
        
    def theme_balance(theme_counts_dict):
        return ui.div( [
            StyleService.one_theme(theme_name, theme_counts_dict[theme_name])
            for theme_name in theme_counts_dict],
        )

    def box_of_themes(themes, css_class = ""):
        return ui.div([StyleService.single_theme(theme, len(themes)) 
                       for theme in themes], 
                      style= StyleService.style_theme_box(len(themes))
                    ).add_class(css_class)


    def name_shorter(long_name):
        shorter_name =  long_name.replace("health and social care", "H&SC").replace("Health and Social Care", "H&SC")
        shorter_name = shorter_name.replace("Introduction", "Intro")
        return shorter_name

    def course_as_card(course_info, show = True, buttons = [], dissertation = False, selected = False):
        name_label = StyleService.name_shorter(course_info.name) #+ " " + self.course_info.id
        
        css_class = "course-box"
        css_class += " dissertation-box" if dissertation else ""
        css_class += " disabled-background" if selected else ""

        return ui.div( 
                        ui.div(  name_label, "*" if course_info.is_compulsory_course else None),
                        ui.div( 
                            ui.div(  *[button for button in buttons]   ),
                            style = "margin:0px; padding:0px",
                            hidden = (dissertation)
                        ),
                        StyleService.box_of_course_metainfo(course_info) ,
                         hidden = (not show)
        ).add_class(css_class)



    def info_card_for_course(course_info):
        more_info_card = (ui.div(
                                ui.row(
                                    ui.div(
                                        {"style": "font-weight: bold"},
                                        ui.p("Course Information"),
                                    )   
                                ),
                                ui.div(ui.tags.b("*COMPULSORY COURSE*")) if course_info.is_compulsory_course else None,
                                ui.div(ui.tags.b("name: "), f"{ course_info.name}"),
                                ui.div(ui.tags.b("id: "), course_info.drps_id),
                                ui.div(ui.tags.b("Credits: "), course_info.credits),
                                ui.div(ui.tags.b("Notes: "), course_info.notes ) if len(course_info.notes)>0 else None,
                                ui.div(ui.tags.b("Description: "), course_info.description) if len(course_info.description)>0 else None,
                                ui.div(ui.tags.b("Assessement: "), course_info.assessment) if len(course_info.assessment)>0 else None,
                                ui.div(ui.tags.b("Years: "), course_info.years, ui.tags.b("Blocks: "), course_info.blocks),
                                ui.div(ui.tags.b("Has prerequisites: "), course_info.has_pre_req_id ) if len(course_info.has_pre_req_id)>0 else None,
                                ui.div(ui.tags.b("Themes: "), ", ".join(course_info.themes)),
                                ui.div(ui.tags.b("Programming in: "), ", ".join(course_info.prog_lang)) if len(course_info.prog_lang)>0 else None,
                                ui.div( StyleService.box_of_themes(course_info.themes, "meta-box-half-bottom")),
                                ui.row(ui.tags.a("View this course on DRPS", href=course_info.link, target="_blank"))
                            ))
        return more_info_card
    
