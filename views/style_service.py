from shiny import  ui
import pandas as pd
from faicons import icon_svg as icon

class StyleService:
    themes = []
    def __init__(self):
        pass

    def style_course_box():
        return "padding: 10px 22px 10px 10px;;  border: 1px solid black; margin: 2px; position:relative;"
    
    def style_course_box_not_selected():
        return "padding: 10px; border: 1px dashed grey; margin: 2px;"
    
    def style_section_box():
        return "padding: 10px; border: 1px solid grey;"
    
    def style_theme_box(number_of_items = 1):
        item_width = 24
        max_in_row = 4
        if number_of_items > max_in_row:
            number_of_items = max_in_row
        return f"display:flex;  flex-wrap: wrap-reverse; width: {item_width*number_of_items}px;"
   
    def style_metainfo_box():
        return "position: absolute; right: 0px; height: 100%; top: 0px ; display:block;"
    
     
    def style_theme_single_size(how_many_themes):
        return f"width: 24px;height: 24px; text-align:center;"
    
         
    def style_theme_single_size_with_count(how_many_themes):
        return f"width: 24px;height: 48px; text-align:center;"

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

    def style_highlighted_link():
        return "background-color: #ffff00; padding: 0px 10px;"
    
    def style_meta_box_half_bottom():
        return "right: 0px; bottom: 0px; position:absolute;"
   
    def single_theme(theme_id, how_many_vertical, text=None):
        if text == None:
            extra_style = StyleService.style_theme_single_size(how_many_vertical)
        else:
            extra_style = StyleService.style_theme_single_size_with_count(how_many_vertical)

        text = text if text  else f"{StyleService.get_theme(theme_id).emoji}"
        return  ui.div(text, 
                      style=StyleService.style_theme_single(theme_id)+extra_style),
    
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
                StyleService.box_of_themes(course_info.themes, StyleService.style_meta_box_half_bottom()),
                style= StyleService.style_metainfo_box()
            ), more_info_card )
        

    def one_theme(theme_id, count):
        theme = StyleService.get_theme(theme_id)
        return ui.div( 
            f"{count} : {theme.emoji} {theme.name}",
            # f"{theme['description']}",
            style=f"background-color:{theme.color}; color:{theme.textcolor};",
        )
        
    def theme_balance(theme_counts_dict):
        return ui.div( [
            StyleService.one_theme(theme_name, theme_counts_dict[theme_name])
            for theme_name in theme_counts_dict],
        )

    def box_of_themes(themes, extra_styles = ""):
        return ui.div([StyleService.single_theme(theme, len(themes)) 
                       for theme in themes], 
                      style= StyleService.style_theme_box(len(themes)) +extra_styles)


    def name_shorter(long_name):
        shorter_name =  long_name.replace("health and social care", "H&SC").replace("Health and Social Care", "H&SC")
        shorter_name = shorter_name.replace("Introduction", "Intro")
        return shorter_name
    
    def course_as_card(course_info, show = True, buttons = [], dissertation = False):
        name_label = StyleService.name_shorter(course_info.name) #+ " " + self.course_info.id
        extra_styles = "padding-bottom: 80px" if dissertation else ""
        # credits = f"{self.course_info.credits} cred."
        return ui.div( 
                        ui.div(  name_label, "*" if course_info.is_compulsory_course else None),
                        ui.div( 
                            ui.div(  *[button for button in buttons]   ),
                            style = "margin:0px; padding:0px" ,
                            hidden = (dissertation)
                        ),
                        StyleService.box_of_course_metainfo(course_info) ,
                        # StyleService.box_of_themes(self.course_info.themes),
                  
                         style= StyleService.style_course_box()+ extra_styles,
                         hidden = (not show)
        )



    def info_card_for_course(course_info):
        more_info_card = (ui.div(
                                ui.row(ui.div(
                                    {"style": "font-weight: bold"},
                                    ui.p("Course Information"),
                                ),),
                                ui.div(ui.tags.b("*COMPULSORY COURSE*")) if course_info.is_compulsory_course else None,
                                ui.div(ui.tags.b("name: "), f"{ course_info.name}"),
                                ui.div(ui.tags.b("id: "), course_info.drps_id),
                                ui.div(ui.tags.b("Credits: "), course_info.credits),
                                ui.div(ui.tags.b("Notes: "), course_info.notes ) if len(course_info.notes)>0 else None,
                                ui.div(ui.tags.b("Years: "), course_info.years),
                                ui.div(ui.tags.b("Blocks: "), course_info.blocks),
                                ui.div(ui.tags.b("Has prerequisites: "), course_info.has_pre_req_id ) if len(course_info.has_pre_req_id)>0 else None,
                                ui.div(ui.tags.b("Themes: "), ", ".join(course_info.themes)),
                                ui.div(ui.tags.b("Programming in: "), ", ".join(course_info.prog_lang)) if len(course_info.prog_lang)>0 else None,
                                ui.div( StyleService.box_of_themes(course_info.themes, StyleService.style_meta_box_half_bottom())),
                                ui.row(ui.tags.a("View this course on DRPS", href=course_info.link, target="_blank"))
                            ))
        return more_info_card
    
