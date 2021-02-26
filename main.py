
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
generator = calculations.data_generator(parameters["outside_temperature"], parameters["outside_temperature"], constants, parameters)

constants['k_p'] = 0.5


data = ColumnDataSource(dict(time=[], control_value=[], airflow_volume=[], cpu_temperature=[], assigned_temperature=[], outside_temperature=[], max_airflow_volume=[]))

print("01\n")

def callback():
    temp = next(generator)
    data.stream({"time": [temp[0]], "control_value": [temp[1]], "airflow_volume": [temp[2]], "cpu_temperature": [temp[4]], "assigned_temperature": [parameters["assigned_temperature"]], "outside_temperature": [parameters["outside_temperature"]], "max_airflow_volume": [parameters["fan_number"]*constants["s"]*constants["p"]]}, 1000)


def simulation_reset():
    temp = generator.send(True)
    data.data = {"time": [temp[0]], "control_value": [temp[1]], "airflow_volume": [temp[2]], "cpu_temperature": [temp[4]], "assigned_temperature": [parameters["assigned_temperature"]], "outside_temperature": [parameters["outside_temperature"]], "max_airflow_volume": [parameters["fan_number"]*constants["s"]*constants["p"]]}


def update_outsideTemp(attr, old, new):
    parameters["outside_temperature"] = new

def update_targetTemp(attr, old, new):
    parameters["assigned_temperature"] = new

def update_numberOfFans(attr, old, new):
    parameters["fan_number"] = new

def update_cpuPower(attr, old, new):
    parameters["generated_heat"] = (new/100)*2.0

print("02\n")

temp_plot = figure(plot_width=800, plot_height=400, x_axis_type='datetime', tools=[], title="Temperatury w układzie")

temp_plot.line(source=data, x='time', y='cpu_temperature', legend_label = "Temperatura procesora")
temp_plot.line(source=data, x='time', y='assigned_temperature', color="red", legend_label="Temperatura zadana")
temp_plot.line(source=data, x='time', y='outside_temperature', color="green", legend_label="Temperatura otoczenia")
temp_plot.xaxis.axis_label = "Czas"
temp_plot.yaxis.axis_label = "Temperatura [*C]"
temp_plot.title.text = "Temperatury w układzie"
temp_plot.legend.location = "bottom_left"
temp_plot.toolbar_location = None

temp2_plot = figure(plot_width=800, plot_height=400, x_axis_type='datetime', tools=[], title="Temperatura procesora")

temp2_plot.line(source=data, x='time', y='cpu_temperature', legend_label = "Temperatura procesora")
temp2_plot.xaxis.axis_label = "Czas"
temp2_plot.yaxis.axis_label = "Temperatura [*C]"
temp2_plot.title.text = "Temperatura procesora"
temp2_plot.legend.location = "bottom_left"
temp2_plot.toolbar_location = None

err_plot = figure(plot_width=800, plot_height=400, x_axis_type='datetime', tools=[], title="Wielkość sterująca")

err_plot.line(source=data, x='time', y='control_value', color='orange', legend_label = "Wielkość sterująca")
#err_plot.line(source=data, x='time', y=0, color='green')
#err_plot.line(source=data, x='time', y=-1, color='red')
err_plot.xaxis.axis_label = "Czas"
err_plot.yaxis.axis_label = "Wielkość sterująca"
err_plot.title.text = "Wielkość sterująca"
err_plot.legend.location = "bottom_left"
err_plot.toolbar_location = None


reg_plot = figure(plot_width=800, plot_height=400, x_axis_type='datetime', tools=[], title="Przepływ powietrza")

reg_plot.line(source=data, x='time', y='airflow_volume', legend_label = "Przepływ powietrza")
reg_plot.line(source=data, x='time', y=0, color='green', legend_label = "Minimalny przepływ") 
reg_plot.line(source=data, x='time', y='max_airflow_volume', color='red', legend_label = "Maksymalny przepływ")
reg_plot.xaxis.axis_label = "Czas"
reg_plot.yaxis.axis_label = "Przepływ powietrza [m^3]"
reg_plot.title.text = "Przepływ powietrza"
reg_plot.legend.location = "bottom_left"
reg_plot.toolbar_location = None


outsideTempSlider = Slider(start = -10, end = 50, value = 20, step = 1, title="Temperatura otoczenia")
targetTempSlider = Slider(start = -10, end = 100, value = 50, step = 1, title="Temperatura docelowa")
numberOfFansSlider = Slider(start = 1, end = 5, value = 1, step = 1, title="Liczba wentylatorów")
cpuPowerSlider = Slider(start = 0, end = 100, value = 50, step = 1, title="Moc procesora [%]")
resetButton = Button(label="Reset")
widgetsTitle = Div(text="""<center><b>Panel kontrolny</b></center>""")

outsideTempSlider.on_change('value_throttled', update_outsideTemp)
targetTempSlider.on_change('value_throttled', update_targetTemp)
numberOfFansSlider.on_change('value_throttled', update_numberOfFans)
cpuPowerSlider.on_change('value_throttled', update_cpuPower)
resetButton.on_click(simulation_reset)

inputs = column([widgetsTitle, targetTempSlider, outsideTempSlider, numberOfFansSlider, cpuPowerSlider, resetButton], width=300)

#curdoc().theme = 'dark_minimal'
grid = gridplot([[temp_plot, err_plot], [temp2_plot, reg_plot]], toolbar_location=None)
#grid.toolbar_location = None
curdoc().add_root(row(inputs, grid))
curdoc().title = "CPU Cooler Simulator"
curdoc().add_periodic_callback(callback, 1)

