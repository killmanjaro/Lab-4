
import requests
import json
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import  tkinter.messagebox  as  tkmb
import os
import time
import threading

# Alyssa Goldgeisser
# Lab 4
# Threading, Multiprocessing, and OS



#old code
'''
city_dict = {

    'North Bay': ('Napa', 'Sonoma'),
    'The Coast': ('Santa+Cruz', 'Monterey'),
    'East Bay': ('Berkeley', 'Livermore'),
    'Peninsula': ('San+Francisco', 'San+Mateo'),
    'South Bay': ('San+Jose', 'Los+Gatos')

    }

new_data = {}
def get_coordinates(city_name): 
''' # does an api call given the city name, returning the latitude and lognitude
'''
    state = 'California'
    response = requests.get(f'https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=10&language=en&format=json')
    data = response.json()
    for result in data['results']:
        if result['admin1'] == state:
            new_data[result['name']] = (result['latitude'], result['longitude'])
        else:
            pass
        
start_serial = time.time()
for key in city_dict:
    try:
        long, lat = get_coordinates(city_dict[key][0])
        new_data[city_dict[key][0]] = (long, lat)
    except TypeError:
        pass
    
    try:
        long1, lat1 = get_coordinates(city_dict[key][1])
        new_data[city_dict[key][1]] = (long1, lat1)
    except TypeError:
        pass
end_serial = time.time()
print('serial time:',end_serial-start_serial)
'''

#new code using threads
#'''
def geo_coding_file():
    geocoding_endpoint = "https://geocoding-api.open-meteo.com/v1/search"
    city_dict = {

        'North Bay': ('Napa', 'Sonoma'),
        'The Coast': ('Santa+Cruz', 'Monterey'),
        'East Bay': ('Berkeley', 'Livermore'),
        'Peninsula': ('San+Francisco', 'San+Mateo'),
        'South Bay': ('San+Jose', 'Los+Gatos')

        }
    
    display_dict = {
        'North Bay': ('Napa', 'Sonoma'),
        'The Coast': ('Santa Cruz', 'Monterey'),
        'East Bay': ('Berkeley', 'Livermore'),
        'Peninsula': ('San Francisco', 'San Mateo'),
        'South Bay': ('San Jose', 'Los Gatos')

            }


    new_data = {}
    geocoding_start = time.time()
    lock = threading.Lock()

    def get_coordinates(city_name): 
        ''' same as above, takes city_name reutrns latitude and logitude '''
        state = 'California'
        response = requests.get(f'https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=10&language=en&format=json')
        data = response.json()
        for result in data['results']:
            if result['admin1'] == state:
                return result['name'], (result['latitude'], result['longitude'])
            else:
                pass
        return city_name, None

    def process_city(city):
        '''  creates dictionary from city name and coordinates'''
        city_name, coordinates = get_coordinates(city)
        if coordinates:
            with lock:
                try:
                    new_data[city_name] = coordinates
                except ValueError:
                    pass
    
    threads = []
            

    for region in city_dict.values():
        for city in region:
            thread = threading.Thread(target=process_city, args=(city,))
            thread.start()
            threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    geocoding_end = time.time()
    print('geocoding time:',geocoding_end-geocoding_start)

    with open('long_latitude.json', 'w') as f:
        json.dump(new_data, f, indent=4)

    return display_dict
#'''

class MainWin(tk.Tk) :
    def __init__(self, file) :
        ''' constructor for MainWin class, loads json file and creates main window'''
        super().__init__() 
        self.location_list = []
        self.save_dict = {}
        self.title("Travel Weather App")

        with open('long_latitude.json', 'r') as f:
            self.data = json.load(f)

        with open(file, 'r') as file:
            self.city_D = json.load(file)



        self.label = tk.Label(self, text="Look up weather in your destination", font=("Helvetica", 14, "bold"), fg='blue')
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.label2 = tk.Label(self, text="Select destinations then click submit", font=("Helvetica", 10), fg='blue')
        self.label2.grid(row=1, column=0, padx=10, pady=10)
        
        self.button = tk.Button(self, text="Submit")
        self.button.bind("<Button 1>", lambda event: self.submit())
        self.button.grid(row=3, column = 0, padx=10,pady=10)

        self.listbox = tk.Listbox(self, selectmode='multiple')

        for index, element in enumerate(self.city_D):
            self.listbox.insert(index, self.city_D[element][0])
            self.listbox.insert(index, self.city_D[element][1])

        self.listbox.grid(row=2, column=0, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>")

    
    def get_weather(self, city_name):
        ''' calls the api using latitude and longitude and gets response, from there creates dictionary entry '''
        lat, long = self.data[city_name]
        response = requests.get(f'https://api.open-meteo.com/v1/gfs?latitude={lat}&longitude={long}&daily=temperature_2m_max,temperature_2m_min,uv_index_max,wind_speed_10m_max&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=America%2FLos_Angeles&start_date=2024-05-29&end_date=2024-06-02')
        response = response.json()   

        weather_dict = {
            city_name: [
                response['daily']['time'],
                response['daily']['temperature_2m_max'],
                response['daily']['temperature_2m_min'],
                response['daily']['wind_speed_10m_max'],
                response['daily']['uv_index_max']
            ]
        }
        return weather_dict

    def selectinfo(self) :
        ''' selects info from the listbox and appends it to location list'''
        tuple = self.listbox.curselection()
        for i in [*list(tuple)]:
            location = self.listbox.get(i)
            self.location_list.append(location)

    def submit(self):
        ''' function for submiting data from selected entries in the listbox, creates display windows'''
        self.selectinfo()
        self.start_time = time.time()
        for item in self.location_list:
            self.d = DisplayWin(item)
        self.end_time = time.time()
        print('serial start vs end:',self.end_time-self.start_time)
        self.location_list.clear()
        self.listbox.selection_clear(0, END)

    def confirm(self):
        ''' confirm on exit function, saves data into a txt file if user wishes'''
        if bool(self.save_dict) == True:
            choice = tkmb.askokcancel("Save", "Save your results in a directory of your choice?", parent=app)
            if choice == True :
                self.save_weather_data()
                app.destroy()   # close GUI window
                app.quit()      # end window object
            else:
                app.destroy()   # close GUI window
                app.quit()      # end window object
        else:
            app.destroy()   # close GUI window
            app.quit()      # end window object


    def save_weather_data(self):
        ''' function that saves the data '''
        directory = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Directory")
        if directory:
            file_path = os.path.join(directory, "weather.txt")
            with open(file_path, "w") as file:
                for key in self.save_dict:
                    file.write(f'{key}\n')
                    file.write(f'{self.save_dict[key][0]}\n')
                    file.write(f'{self.save_dict[key][1]}\n')
                    file.write(f'{self.save_dict[key][2]}\n')
                    file.write(f'{self.save_dict[key][3]}\n')
                    file.write(f'{self.save_dict[key][4]}\n')
                    


class DisplayWin(tk.Toplevel):
    def __init__(self, location):
        ''' constructor for the display window class, takes location and creates window'''
        super().__init__()
        self.location = location
        self.title(f'City Weather')
        #self.start_time = time.time()
        #self.t = threading.Thread(target=self.run_api_call)
        #self.t.start()
        self.run_api_call()

    def run_api_call(self):
        ''' runs the api call'''
        data = app.get_weather(self.location)
        self.display_data(data)

        

    def display_data(self, location_dict):
        ''' displays the data given a dictionary'''
        #end_time = time.time()
        #print('weather data multi-threading',end_time-self.start_time)
        app.save_dict.update(location_dict)
        self.label = tk.Label(self, text=f'Weather for {self.location}', fg='blue')
        self.label.grid(row=0, column=2, padx=5, pady=5)

        self.datelabel = tk.Label(self, text='Date', fg='blue')
        self.datelabel.grid(row=1, column=0, padx=5, pady=5)

        self.datelistbox = tk.Listbox(self, height=5, width=10)
        self.datelistbox.grid(row=2, column=0, padx=5, pady=5)

        for date in location_dict[self.location][0]:
            self.datelistbox.insert(tk.END, date)
        
        self.highlabel = tk.Label(self, text='High', fg='blue')
        self.highlabel.grid(row=1, column=1, padx=5, pady=5)

        self.highlistbox = tk.Listbox(self, height=5, width=10)
        self.highlistbox.grid(row=2, column=1, padx=5, pady=5)

        for high in location_dict[self.location][1]:
            self.highlistbox.insert(tk.END, high)
        
        self.lowlabel = tk.Label(self, text='Low',  fg='blue')
        self.lowlabel.grid(row=1, column=2, padx=5, pady=5)

        self.lowlistbox = tk.Listbox(self, height=5, width=10)
        self.lowlistbox.grid(row=2, column=2, padx=5, pady=5)

        for low in location_dict[self.location][2]:
            self.lowlistbox.insert(tk.END, low)

        self.windlabel = tk.Label(self, text='Wind', fg='blue')
        self.windlabel.grid(row=1, column=3, padx=5, pady=5)

        self.windlistbox = tk.Listbox(self, height=5, width=10)
        self.windlistbox.grid(row=2, column=3, padx=5, pady=5)

        for wind in location_dict[self.location][3]:
            self.windlistbox.insert(tk.END, wind)

        self.uvlabel = tk.Label(self, text='UV',  fg='blue')
        self.uvlabel.grid(row=1, column=4, padx=5, pady=5)

        self.uvlistbox = tk.Listbox(self, height=5, width=10)
        self.uvlistbox.grid(row=2, column=4, padx=5, pady=5)

        for uv in location_dict[self.location][4]:
            self.uvlistbox.insert(tk.END, uv)


FILENAME = 'my_new_json_please_work3.json'    
if os.path.exists(FILENAME):
    pass

else:
    my_dict = geo_coding_file()
    with open('my_new_json_please_work3.json', 'w') as f:
        json.dump(my_dict, f, indent=4)
    

app = MainWin(FILENAME)  
app.protocol("WM_DELETE_WINDOW", app.confirm)
app.mainloop()

'''
for weather data, I am making 10 requests
                serial   multithreading
geocoding data   11.46      2.57
weather data      10.22     2.45 
'''