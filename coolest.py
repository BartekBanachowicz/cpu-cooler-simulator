
'''
To run:
python -m bokeh serve iex.py

'''

print("XD\n")

import calculations
import io
import requests
#import pandas as pd
#import pyEX
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import TextInput, Button, Select, Slider, Div
#from bokeh.themes import built_in_themes
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, widgetbox, gridplot, column


constants = calculations.generate_constants()
parameters = calculations.generate_parameters()
generator = calculations.data_iterator(parameters["assigned_temperature"], 0.0, parameters["outside_temperature"], parameters["outside_temperature"], constants, parameters)


data = ColumnDataSource(dict(time=[0.0], control_value=[0.0], airflow_volume=[0.0], cpu_temperature=[parameters["outside_temperature"]]))

print("01\n")

def callback():
    temp = next(generator)
    data.stream({"time": [temp[0]], "control_value": [temp[1]], "airflow_volume": [temp[2]], "cpu_temperature": [temp[4]]}, 5000)


'''def update_ticker():
    global TICKER
    TICKER = ticker_textbox.value
    price_plot.title.text = "IEX Real-Time Price: " + ticker_textbox.value
    data.data = dict(time=[], display_time=[], price=[])

    return'''


def update_outsideTemp(attr, old, new):
    parameters["outside_temperature"] = new

def update_targetTemp(attr, old, new):
    parameters["assigned_temperature"] = new

def update_numberOfFans(attr, old, new):
    parameters["fan_number"] = new

def update_cpuPower(attr, old, new):
    parameters["generated_heat"] = new

print("02\n")

hover = HoverTool(tooltips=[("Time", "@display_time"), ("IEX Real-Time Price", "@price")])

temp_plot = figure(plot_width=800, plot_height=400, x_axis_type='datetime', tools=[hover], title="Temperatura procesora")

temp_plot.line(source=data, x='time', y='cpu_temperature')
temp_plot.xaxis.axis_label = "Time"
temp_plot.yaxis.axis_label = "Temperatura [*C]"
temp_plot.title.text = "Temperatura procesora"

err_plot = figure(plot_width=800, plot_height=400, x_axis_type='datetime', tools=[hover], title="Control value")

err_plot.line(source=data, x='time', y='control_value')
err_plot.xaxis.axis_label = "Time"
err_plot.yaxis.axis_label = "Control value"
err_plot.title.text = "Control value"

reg_plot = figure(plot_width=800, plot_height=400, x_axis_type='datetime', tools=[hover], title="Airflow volume")

reg_plot.line(source=data, x='time', y='airflow_volume')
reg_plot.xaxis.axis_label = "Time"
reg_plot.yaxis.axis_label = "Airflow volume"
reg_plot.title.text = "Airflow volume"


outsideTempSlider = Slider(start = -10, end = 50, value = 20, step = 1, title="Temperatura otoczenia")
targetTempSlider = Slider(start = -10, end = 100, value = 50, step = 1, title="Temperatura docelowa")
numberOfFansSlider = Slider(start = 1, end = 5, value = 1, step = 1, title="Liczba wentylatorów")
cpuPowerSlider = Slider(start = 0, end = 100, value = 1, step = 1, title="Moc procesora [%]")
widgetsTitle = Div(text="""<center><b>Panel kontrolny</b></center>""")

outsideTempSlider.on_change('value', update_outsideTemp)
targetTempSlider.on_change('value', update_targetTemp)
numberOfFansSlider.on_change('value', update_numberOfFans)
cpuPowerSlider.on_change('value', update_cpuPower)

'''ticker_textbox = TextInput(placeholder="Ticker")
update = Button(label="Update")
update.on_click(update_ticker)'''

inputs = widgetbox([widgetsTitle, targetTempSlider, outsideTempSlider, numberOfFansSlider, cpuPowerSlider], width=300)

#curdoc().theme = 'dark_minimal'
grid = gridplot([[temp_plot, err_plot], [None, reg_plot]])
curdoc().add_root(row(inputs, grid))
curdoc().title = "CPU Cooler Simulator"
curdoc().add_periodic_callback(callback, 1)

