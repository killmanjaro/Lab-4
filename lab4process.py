
import requests
import json
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import  tkinter.messagebox  as  tkmb
import os
import time
import threading
import multiprocessing as mp


#new code using pool
#'''

geocoding_endpoint = "https://geocoding-api.open-meteo.com/v1/search"
city_dict = {

    'North Bay': ('Napa', 'Sonoma'),
    'The Coast': ('Santa+Cruz', 'Monterey'),
    'East Bay': ('Berkeley', 'Livermore'),
    'Peninsula': ('San+Francisco', 'San+Mateo'),
    'South Bay': ('San+Jose', 'Los+Gatos')

    }

new_data = {}
geocoding_start = time.time()

def get_coordinates(city_name): 
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
    city_name, coordinates = get_coordinates(city)
    if coordinates:
        try:
            return city_name, coordinates
        except ValueError:
            pass

def dict_result(result):
    key, value = result
    results[key] = value
#'''

def get_weather(city_name, data, q):
    ''' calls the api using latitude and longitude and gets response, from there creates dictionary entry '''    
    lat, long = data[city_name]
    response =  requests.get(f'https://api.open-meteo.com/v1/gfs?latitude={lat}&longitude={long}&daily=temperature_2m_max,temperature_2m_min,uv_index_max,wind_speed_10m_max&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=America%2FLos_Angeles&start_date=2024-05-29&end_date=2024-06-02')
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
    q.put((weather_dict))



class MainWin(tk.Tk) :
    def __init__(self) :
        ''' constructor for MainWin class, loads json file and creates main window'''
    
        super().__init__() 
        self.location_list = []
        self.save_dict = {}
        self.title("Travel Weather App")

        with open('long_latitude.json', 'r') as f:
            self.data = json.load(f)

        self.label = tk.Label(self, text="Look up weather in your destination", font=("Helvetica", 14, "bold"), fg='blue')
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.label2 = tk.Label(self, text="Select destinations then click submit", font=("Helvetica", 10), fg='blue')
        self.label2.grid(row=1, column=0, padx=10, pady=10)
        
        self.button = tk.Button(self, text="Submit")
        self.button.bind("<Button 1>", lambda event: self.submit())
        self.button.grid(row=3, column = 0, padx=10,pady=10)

        self.listbox = tk.Listbox(self, selectmode='multiple')

        city_list = ['North Bay: Napa',
                     'North Bay: Sonoma',
                     'The Coast: Santa Cruz',
                     'The Coast: Monterey',
                     'East Bay: Berkeley',
                     'East Bay: Livermore',
                     'Peninsula: San Francisco',
                     'Peninsula: San Mateo',
                     'South Bay: San Jose',
                     'South Bay: Los Gatos']

        for index, element in enumerate(city_list):
            self.listbox.insert(index, element)

        self.listbox.grid(row=2, column=0, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>")


    def selectinfo(self) :
        ''' selects info from the listbox and appends it to location list'''
        tuple = self.listbox.curselection()
        for i in [*list(tuple)]:
            _, location = self.listbox.get(i).split(': ', 1)
            self.location_list.append(location)

    def submit(self):
        ''' function for submiting data from selected entries in the listbox, creates display windows'''
        self.selectinfo()
        mygeostart = time.time()
        q = mp.Queue()
        processes = []
        
        for city in self.location_list:
            p = mp.Process(target=get_weather, args=(city, self.data, q))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        while not q.empty():
            data = q.get()
            if data:
                DisplayWin(data)

        mygeoend = time.time()
        print('multi processing weather data end:',mygeoend-mygeostart)

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
    def __init__(self, data):
        ''' constructor for the display window class, takes location and creates window'''
        super().__init__()
        self.data = data
        self.title(f'City Weather')
        self.display_data(data)

    def display_data(self, location_dict):
        ''' displays the data given a dictionary'''
        end_time = time.time()
        app.save_dict.update(location_dict)
        key = list(location_dict.keys())[0]
        self.label = tk.Label(self, text=f'Weather for {key}', fg='blue')
        self.label.grid(row=0, column=2, padx=5, pady=5)

        self.datelabel = tk.Label(self, text='Date', fg='blue')
        self.datelabel.grid(row=1, column=0, padx=5, pady=5)

        self.datelistbox = tk.Listbox(self, height=5, width=10)
        self.datelistbox.grid(row=2, column=0, padx=5, pady=5)

        for date in location_dict[key][0]:
            self.datelistbox.insert(tk.END, date)
        
        self.highlabel = tk.Label(self, text='High', fg='blue')
        self.highlabel.grid(row=1, column=1, padx=5, pady=5)

        self.highlistbox = tk.Listbox(self, height=5, width=10)
        self.highlistbox.grid(row=2, column=1, padx=5, pady=5)

        for high in location_dict[key][1]:
            self.highlistbox.insert(tk.END, high)
        
        self.lowlabel = tk.Label(self, text='Low',  fg='blue')
        self.lowlabel.grid(row=1, column=2, padx=5, pady=5)

        self.lowlistbox = tk.Listbox(self, height=5, width=10)
        self.lowlistbox.grid(row=2, column=2, padx=5, pady=5)

        for low in location_dict[key][2]:
            self.lowlistbox.insert(tk.END, low)

        self.windlabel = tk.Label(self, text='Wind', fg='blue')
        self.windlabel.grid(row=1, column=3, padx=5, pady=5)

        self.windlistbox = tk.Listbox(self, height=5, width=10)
        self.windlistbox.grid(row=2, column=3, padx=5, pady=5)

        for wind in location_dict[key][3]:
            self.windlistbox.insert(tk.END, wind)

        self.uvlabel = tk.Label(self, text='UV',  fg='blue')
        self.uvlabel.grid(row=1, column=4, padx=5, pady=5)

        self.uvlistbox = tk.Listbox(self, height=5, width=10)
        self.uvlistbox.grid(row=2, column=4, padx=5, pady=5)

        for uv in location_dict[key][4]:
            self.uvlistbox.insert(tk.END, uv)
        
        

if __name__ == '__main__':
    #'''
    city_names = [city for cities in city_dict.values() for city in cities]
    manager = mp.Manager()
    results = manager.dict()
    
    process_start = time.time()
    pool = mp.Pool(processes=10)
    for city in city_names:
        pool.apply_async(process_city, args=(city,), callback=dict_result)
    
    pool.close()
    pool.join()
    process_end = time.time()
    print('pool multi-processing:',process_end - process_start)

    final_results = dict(results)


    with open('long_latitude.json', 'w') as f:
        json.dump(final_results, f, indent=4)
    
    #'''
    app = MainWin()
    app.protocol("WM_DELETE_WINDOW", app.confirm)
    app.mainloop()


'''
for weather data, I am making 10
                serial   multithreading    multiprocessing
geocoding data   11.46      2.57                3.64
weather data     10.23      2.45                3.66
                             
                             
'''


# multithreading > multiprocessing > serial