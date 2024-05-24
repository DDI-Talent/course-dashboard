from shiny import App, render, ui

app_ui = ui.page_fixed(
    ui.input_slider("val", "Slider label", min=0, max=100, value=50),
    ui.output_text_verbatim("slider_val"),
    ui.output_table("table_with_numbers")
)

def server(input, output, session):
    @render.text
    def slider_val():
        return f"Slider value: {input.val()}"
    
    @render.table
    def table_with_numbers():
        return [1,2,3]

app = App(app_ui, server)