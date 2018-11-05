from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import csv
import matplotlib.pyplot as plt, mpld3
import matplotlib.cm
import json
from haversine import haversine
import math
import numpy as np
import seaborn as sns
import pandas as pd

#read the given csv file and store in array format into data
data = list(csv.reader(open('metro-bike-share-trip-data.csv'))) #original data
#the below data is retrieved from the metro-bike-share website. It is used in 
#the season function because our original data set does not give us much data
#for the Spring term, therefore the data was creating strange graphs
data1 = list(csv.reader(open('metro-bike-share-trips-2018-q1.csv'))) #quarter 1
data2 = list(csv.reader(open('metro-bike-share-trips-2018-q2.csv'))) #quarter 2
data3 = list(csv.reader(open('metro-bike-share-trips-2018-q3.csv'))) #quarter 3
data4 = list(csv.reader(open('metro-bike-share-trips-2017-q4-v2.csv'))) #quarter 4

sns.set() #set seaborn

# function to determine the percentage of roundtrips vs one-way trips
def type_of_trip():
	types = ["Round Trip", "One Way"] #declare axis labels used in plotting
	count = [0,0] #declare empty count array
	for i in range(1,len(data)): #iterate
		if (data[i][12] == "Round Trip"): #access the trip field from the data
			count[0] +=1 #count[0] value represents the amount of round trips
		else:
			count[1] += 1 #count[1] value represents the amount of one-ways

	#plot pie char and export to file in html_plots folder -> this html is them embedded into
	#our web app
	fig, ax1 = plt.subplots()
	explode = (.05,.05)
	plt.pie(count, explode=explode, labels=types, 
		autopct='%1.1f%%', shadow=True, startangle=30)
	ax1.axis('equal')

	#For this and following functions, we export our figure to a file located in the
	#html_plots folder using the mpld3 library. This html code makes an interactive
	#plot, and we embed and format each graph in the respective page we want it in

	html = mpld3.fig_to_html(fig)
	with open("html_plots/type_of_trip.html", "w") as myfile:
		myfile.write(html)

#function that examines the most used bikes (by duration) in the given data
def most_used_bikes():
	count = {} #create dict count
	for i in range(1,len(data)): #iterate for rows 1 to end in data
		key = data[i][10] #retrieve the bike ID
		if key in count: #if the bike ID exists
			count[key] += int(data[i][1])#increment its value by the duration of ride
		else: #if it does not exist
			count[key] = int(data[i][1]) #set the bike ID value to the first duration

	sorted_bikes = sorted(count, key=count.get) #sort our dict of bikes by value
	#determine the top ten bikes for our display
	top_ten_bikes = sorted_bikes[len(sorted_bikes)-10:len(sorted_bikes)]
	#vals array will store the number of rides for each bike
	vals = []
	for i in range(10):
		#for the top ten durations, we divide by 3600 to retrieve the amount of hours
		vals.append((count[top_ten_bikes[i]])/3600)

	#plot the Bike IDs and the total time they have been rode
	fig, ax1 = plt.subplots()
	plt.xlabel("Bike ID")
	plt.ylabel("Number of Hours Rode")
	plt.bar(top_ten_bikes, vals, align='center',color='teal')
	plt.xticks(top_ten_bikes, top_ten_bikes)
	html = mpld3.fig_to_html(fig)
	#write plot to html_plots/most_used_bike.html
	with open("html_plots/most_used_bike.html", "w") as myfile:
		myfile.write(html)

#function to determine relationship between the start time of a trip and its duration
def start_time_vs_duration():
	x  = [i for i in range(0,24)] #declare array to hold time of day value
	durations  = [0 for i in range(0,24)] #durations array hold total duration for each hour
	duration_counts  = [0 for i in range(0,24)] #duration_counts array is to track how many rides in that hour
	for i in range(1, len(data)): #iterate through data
		time = data[i][2] #retrieve the time field
		durations[int(time[11:13])] += int(data[i][1]) #increase the correct hour with the duration
		duration_counts[int(time[11:13])] += 1 #increment the corresponding duration_counts cell

	for i in range(0,24): #iterate for all values in durations
		durations[i] = (durations[i]/(duration_counts[i]))/60 #divide by the number of rides and 60 seconds

	#plot the time of day vs the average duration of a trip 
	fig, ax1 = plt.subplots()
	plt.xlabel("Time of Day")
	plt.ylabel("Average Duration of Trip (Min)")
	plt.plot(x, durations,color='teal', marker='o')
	#xticks allows us to link the hours to the correct time of day
	plt.xticks(x, ["12 AM", "", "", "", "4 AM", "",
	"", "", "8 AM", "", "", "", "12 PM", "", "", "", "4 PM",
	 "", "", "", "8 PM","", "", "11 PM"])
	html = mpld3.fig_to_html(fig)
	#writes to our html_plots file
	with open("html_plots/start_time_vs_duration.html", "w") as myfile:
		myfile.write(html)

#function to calculate the average distance travelled
def average_distance():
	ave_speed = 15.5/3600 #average speed in km/s (from Google data)
	tot_dist = 0 #initialize the total distance travelled
	not_filled = 0 #initialize value to keep track of cells skipped (see below)
	for i in range(1,len(data)): #iterate for all data
		#these checks are in place because some data fields in the csv
		#have no value and cause issues when calculating
		if (data[i][5] != "" and data[i][6] != ""): #check if field valid
			x1 = float(data[i][5]) #store lat and long values of start
			x2 = float(data[i][6])
		else: #if not valid, continue to next data slot
			not_filled += 1 #increment the amount of entries that are invalid
			continue
		if (data[i][7] != "" and data[i][8] != ""):	
			y1 = float(data[i][8]) #store lat and long values of end
			y2 = float(data[i][9])
		else:
			not_filled += 1 #increment the amount of entries that are invalid
			continue

		x = (x1, x2) #for (lat, lon) for start and end point
		y = (y1, y2)

		if (x != y): #check if locations are different (one-way)
			distance = haversine(x, y) #use the haversine function to calculate distance
			tot_dist += distance #add it to the total distance
		else: #if the trip is a round trip
			secs = float(data[i][1]) #retrieve the duration
			distance = ave_speed*secs #multiply ave_speed with time
			tot_dist += distance #add the correct distance

	ave_dist_km = tot_dist/(len(data)-1-not_filled) #calculate the ave_dist in km
	ave_dist_mi = ave_dist_km*0.621371 #calculate it in miles
	#this function was run separately, and the output was used to create an image
	#with the average distance in km and miles

#this function calculates all the seasonal data and plots it 
#(it is quite lengthy) because it relies on a separate data set. This is done
#because the original data set did not include sufficient data for the Spring months
#leading to erroneous graphs that did not properly represent the data
def seasons():
	#Winter, Spring, Summer, Fall
	months = [i for i in range(12)] #declare months array
	count = [0 for i in range(12)] #decalare count for each month
	seasons = ["Winter", "Spring", "Summer", "Fall"] #label array used for graphs
	total_duration = [0 for i in range(12)] #keep track of total duration for each month
	duration_count = [0 for i in range(12)] #keep track of number of rides per month
	#row in pass_type represents pass type count
	#col in pass_type represents season (Winter, Spring, Summer, Fall) in that order
	pass_type = [[0,0,0,0],[0,0,0,0],[0,0,0,0]] #keep track of pass_type
	
	#the following loop is repeated four times for each quarter (data1, data2, data3, data4)
	#this gives us a complete picture of the entire year

	for i in range(1,len(data1)):
		date = data1[i][2] #retrieve the date/time
		month = int(date[5:7]) #retrieve the month
		season = "" #initialize season
		count[month-1] += 1 #increment the count of the right month
		#for this data set, the durations are in minutes
		total_duration[month-1] += int(data1[i][1]) #increment the duration of the month
		duration_count[month-1] += 1 #increment the correct duration count for this month

		pass_variable = 0 #initialize pass_variable
		if (data1[i][11] == '365'): #check to see which type of pass it is
			pass_variable =  0
		if (data1[i][11] == '30'):
			pass_variable = 1
		if (data1[i][11] == '0'):
			pass_variable =  2
		#we check which month we are in, and increment the correct cell in pass_type
		if (month==12 or month<=2):  
			season = "Winter"
			pass_type[pass_variable][0] +=1
		if (3<=month<=5):
			season = "Spring"
			pass_type[pass_variable][1] +=1
		if (6<=month<=8):
			season = "Summer"
			pass_type[pass_variable][2] +=1		
		if (9<=month<=11):
			season = "Fall"
			pass_type[pass_variable][3] +=1
	#repeat for data2
	for i in range(1, len(data2)):
		date = data2[i][2]
		month = int(date[5:7])
		season = ""
		count[month-1] += 1
		total_duration[month-1] += int(data2[i][1]) #data is in minutes
		duration_count[month-1] += 1

		pass_variable = 0
		if (data2[i][11] == '365'):
			pass_variable =  0
		if (data2[i][11] == '30'):
			pass_variable = 1
		if (data2[i][11] == '0'):
			pass_variable =  2

		if (month==12 or month<=2):
			season = "Winter"
			pass_type[pass_variable][0] +=1
		if (3<=month<=5):
			season = "Spring"
			pass_type[pass_variable][1] +=1
		if (6<=month<=8):
			season = "Summer"
			pass_type[pass_variable][2] +=1		
		if (9<=month<=11):
			season = "Fall"
			pass_type[pass_variable][3] +=1
	#repeat for data3
	for i in range(1, len(data3)):
		date = data3[i][2]
		month = int(date[5:7])
		season = ""
		count[month-1] += 1
		total_duration[month-1] += int(data3[i][1]) #data is in minutes
		duration_count[month-1] += 1

		pass_variable = 0
		if (data3[i][11] == '365'):
			pass_variable =  0
		if (data3[i][11] == '30'):
			pass_variable = 1
		if (data3[i][11] == '0'):
			pass_variable =  2

		if (month==12 or month<=2):
			season = "Winter"
			pass_type[pass_variable][0] +=1
		if (3<=month<=5):
			season = "Spring"
			pass_type[pass_variable][1] +=1
		if (6<=month<=8):
			season = "Summer"
			pass_type[pass_variable][2] +=1		
		if (9<=month<=11):
			season = "Fall"
			pass_type[pass_variable][3] +=1
	#repeat for data4
	for i in range(1, len(data4)):
		date = data4[i][2]
		month = int(date[5:7])
		season = ""
		count[month-1] += 1
		total_duration[month-1] += int(data4[i][1]) #data is in minutes
		duration_count[month-1] += 1

		pass_variable = 0
		if (data4[i][11] == '365'):
			pass_variable =  0
		if (data4[i][11] == '30'):
			pass_variable = 1
		if (data4[i][11] == '0'):
			pass_variable =  2

		if (month==12 or month<=2):
			season = "Winter"
			pass_type[pass_variable][0] +=1
		if (3<=month<=5):
			season = "Spring"
			pass_type[pass_variable][1] +=1
		if (6<=month<=8):
			season = "Summer"
			pass_type[pass_variable][2] +=1		
		if (9<=month<=11):
			season = "Fall"
			pass_type[pass_variable][3] +=1

	#ave_duration holds the average duration for each month
	ave_duration = []
	for i in range(12):
		if (duration_count[i] != 0): #make sure we are not dividing by 0
			ave_duration.append((total_duration[i]/duration_count[i]))
		else:
			ave_duration.append(0)

	#plot for types of passes used for each season
	fig, ax1 = plt.subplots()
	barWidth = 0.25
	r1 = np.arange(4)
	r2 = [x + barWidth for x in r1]
	r3 = [x + barWidth for x in r2]
	r4 = [x + barWidth for x in r2]
	plt.bar(r1, pass_type[0], color='b', width=barWidth, edgecolor='white', label='Year')
	plt.bar(r2, pass_type[1], color='g', width=barWidth, edgecolor='white', label='Month')
	plt.bar(r3, pass_type[2], color='y', width=barWidth, edgecolor='white', label='One-Day')
	plt.legend()
	plt.xlabel('Season')
	plt.xticks([r + barWidth for r in range(4)], ['Winter', 'Spring', 'Summer', 'Fall'])
	plt.ylabel("Pass Type Amount")
	for i in range(4):
		ax1.annotate(pass_type[0][i], xy=(i-.15, pass_type[0][i]+700))
	for i in range(4):
		ax1.annotate(pass_type[1][i], xy=(i+.13, pass_type[1][i]+700))
	for i in range(4):
		ax1.annotate(pass_type[2][i], xy=(i+.40, pass_type[2][i]+700))
	html = mpld3.fig_to_html(fig)
	#write to file html_plots/seasons.html
	with open("html_plots/seasons.html", "w") as myfile:
		myfile.write(html)

	#plot for total riders per season
	fig, ax1 = plt.subplots()
	plt.plot(months, count, marker='o')
	plt.xticks(months, ["Jan","","","April","","","July","","","October","",""])
	plt.xlabel("Month")
	plt.ylabel("Number of Rides")
	html = mpld3.fig_to_html(fig)
	#append to our seasons.html file
	with open("html_plots/seasons.html", "a") as myfile:
		myfile.write(html)

	#plot for average duration of ride per season
	fig, ax1 = plt.subplots()
	plt.plot(months, ave_duration, marker='o')
	plt.xticks(months, ["Jan","","","April","","","July","","","October","",""])
	plt.xlabel("Month")
	plt.ylabel("Average Duration of Rides (Minutes)")
	html = mpld3.fig_to_html(fig)
	#append to our seasons.html file
	with open("html_plots/seasons.html", "a") as myfile:
		myfile.write(html)

#function to determine rider frequency (percentage of riders with each pass)
def rider_frequency():
	#declare pass type labels
	types = ["Flex Pass (Year Plan)", "Monthly Pass", "Walk-up"]
	count = [0,0,0] #initialize count list
	for i in range(1, len(data)): #iterate for data
		if (data[i][11] == '365'): #increment the correct count based on the pass
			count[0] +=1
		if (data[i][11] == '30'):
			count[1] += 1 
		if (data[i][11] == '0'):
			count[2] += 1

	#plot pie chart
	fig, ax1 = plt.subplots()
	explode = (.05,.05,.05)
	plt.pie(count, explode=explode, labels=types, 
		autopct='%1.1f%%', shadow=True, startangle=30)
	ax1.axis('equal')
	html = mpld3.fig_to_html(fig)
	#write to html_plot/rider_frequency.html 
	with open("html_plots/rider_frequency.html", "w") as myfile:
		myfile.write(html)

#calculate the most popular start locations
def most_popular_start_loc():
	count = {} #create dict count
	for i in range(1,len(data)): #iterate for rows 1 to end in data
		key = data[i][4] #retrieve stop ID key
		if key in count: #update dict accordingly
			count[key] +=1
		else:
			count[key] = 1

	#sort the dict by value
	sorted_stops = sorted(count, key=count.get)
	#retrieve the top ten stops
	top_ten_stops = sorted_stops[len(sorted_stops)-10:len(sorted_stops)]
	#vals will hold the number of visits for the top ten stops
	vals = []
	for i in range(10):
		vals.append(count[top_ten_stops[i]])

	#create latitude and longitude arrays
	lat = []
	lon = []
	#for the top ten stops, store the latitude and longitude values in the arrays
	for i in range(0, len(top_ten_stops)):
		for j in range(1, len(data)):
			if (data[j][4] == top_ten_stops[i]):
				val_lat = float(data[j][5])
				lat.append(val_lat)
				val_lon = float(data[j][6])
				lon.append(val_lon)
				break

	#the above loop gives us lat and long values. These values were then taken 
	#and embedded into the /templates/popular_locs_map.html file to be used by
	#the Google maps API. Using the API, we can see the location of each one of
	#the stations.

	#plot the most visited stops as a bar graph against the number of visits
	fig, ax1 = plt.subplots()
	plt.title("Most Visited Stops")
	plt.xlabel("Stop ID")
	plt.ylabel("Number of Visits")
	plt.bar(top_ten_stops, vals, align='center',color='teal')
	plt.xticks(top_ten_stops, top_ten_stops)
	html = mpld3.fig_to_html(fig)
	#write our plot to the file html_plots/popular_locs_map.html
	with open("html_plots/popular_start_locs.html", "w") as myfile:
		myfile.write(html)		

#calculated the most popular end station in the same way as above
def most_popular_end_loc():
	count = {} #create dict count
	for i in range(1,len(data)): #iterate for rows 1 to end in data
		key = data[i][7] 
		if key in count:
			count[key] +=1
		else:
			count[key] = 1

	sorted_stops = sorted(count, key=count.get)
	top_ten_stops = sorted_stops[len(sorted_stops)-10:len(sorted_stops)]
	vals = []
	for i in range(10):
		vals.append(count[top_ten_stops[i]])


	lat = []
	lon = []
	for i in range(0, len(top_ten_stops)):
		for j in range(1, len(data)):
			if (data[j][7] == top_ten_stops[i]):
				val_lat = float(data[j][8])
				lat.append(val_lat)
				val_lon = float(data[j][9])
				lon.append(val_lon)
				break

	#the above loop gives us lat and long values. These values were then taken 
	#and embedded into the /templates/popular_locs_map.html file to be used by
	#the Google maps API. Using the API, we can see the location of each one of
	#the stations.

	#plot the popular end locs on bar graph
	fig, ax1 = plt.subplots()
	plt.title("Most Visited Stops")
	plt.xlabel("Stop ID")
	plt.ylabel("Number of Visits")
	plt.bar(top_ten_stops, vals, align='center',color='teal')
	plt.xticks(top_ten_stops, top_ten_stops)
	html = mpld3.fig_to_html(fig)
	#export to file html_plots/popular_end_locs.html
	with open("html_plots/popular_end_locs.html", "w") as myfile:
		myfile.write(html)		

#function to determine relationship between trip type and pass type
def trip_route_passholder():
	pass_type = ["Monthly Pass", "Flex Pass", "Walk-up"] #declare pass_type labels
	#row of trip route are Round Trip, One Way
	#cols of trip route are Monthly Pass, Flex Pass, Walk-up
	trip_route = [[0,0,0], [0,0,0]]
	for i in range(1, len(data)): #iterate through data
		index = 0 #round trip
		if (data[i][12] == "One Way"): #if one-way
			index = 1 #update index
		#accordingly update the correct cell in trip_route
		if (data[i][13] == "Monthly Pass"):
			trip_route[index][0] +=1
		if (data[i][13] == "Flex Pass"):
			trip_route[index][1] +=1
		if (data[i][13] == "Walk-up"):
			trip_route[index][2] +=1

	#plot a bar graph comparing the trip type with the pass
	fig, ax1 = plt.subplots()
	barWidth = 0.25
	r1 = np.arange(3)
	r2 = [x + barWidth for x in r1]
	plt.bar(r1, trip_route[0], color='teal', width=barWidth, edgecolor='white', label='Round Trip')
	plt.bar(r2, trip_route[1], color='orange', width=barWidth, edgecolor='white', label='One Way')
	plt.legend()
	plt.xlabel('Pass Type')
	plt.xticks([r + barWidth/2 for r in range(3)], ['Monthly Pass', 'Flex Pass', 'Walk-up'])
	plt.ylabel("Trip Type")
	html = mpld3.fig_to_html(fig)
	#export to file html_plots/trip_pass.html
	with open("html_plots/trip_route_passholder.html", "w") as myfile:
		myfile.write(html)

#function that analyzes change in bike patterns over the course of the day
def change_in_bikes_over_day():
	#counts array stores the amount of trips for morning, afternoon, evening, night
	#counts = [0,0,0,0] 
	times  = [i for i in range(0,24)] #times array is for times 0-24 (each hour)
	times_counts = [0]*24 #time counts stores amount of trips for each hour
	# morning_locs = [] #_locs arrays store every latitude and longitude pair
	# afternoon_locs = []
	# evening_locs = []
	# night_locs = []
	for i in range(1,len(data)): #iterate through data set
		start_time = data[i][2] #retrieve the start_time
		hour = int(start_time[11:13]) #retrieves the hour based on start_time
		times_counts[hour] += 1 #increment the correct hour

	#Retrieve the top three locations for all hours
	top_three_locs = [["","",""]]*24
	for i in range(0,24): #iterate for hours
	    cur_dict = {} #initialize dict
	    for j in range(1, len(data)):
	        start_time = data[j][2] #retrieve the start_time
	        hour = int(start_time[11:13]) #retrieves the hour based on start_time
	        if (hour == i):
	            loc_key = data[j][4] #starting station ID
	            if loc_key in cur_dict:
	                cur_dict[loc_key] +=1
	            else:
	                cur_dict[loc_key] = 1

	    #sort the stops and find the top three, add it to your top_three_locs array
	    sorted_stops = sorted(cur_dict, key=cur_dict.get)
	    top_three_stops = sorted_stops[len(sorted_stops)-3:len(sorted_stops)]
	    top_three_locs[i] = top_three_stops

	#top_three_locs now holds the top 3 locations for each hour (station ID)
	#we want the latitude and longitude of these stations
	lat = []
	lon = []
	for i in range(0, len(top_three_locs)): #iterate for every hour
	    for j in range(3): #iterate for each station
	        for k in range(1, len(data)): #look for and retrieve the location points
	            if (data[k][4] == top_three_locs[i][j]):
	                val_lat = float(data[k][5])
	                lat.append(val_lat)
	                val_lon = float(data[k][6])
	                lon.append(val_lon)
	                break

	#lat and lon now contain all of the latitude and longitude points
	#This function was run, and the points for 12 PM - 5 PM were printed and embedded
	#into the html for the google map

	#plot of bikes over the course of the day
	fig, ax1 = plt.subplots()
	plt.xlabel("Time of Day")
	plt.ylabel("Number of Trips Taken")
	plt.plot(times, times_counts,color='teal', marker='o')
	plt.xticks(times, ["12 AM", "", "", "", "4 AM", "",
	"", "", "8 AM", "", "", "", "12 PM", "", "", "", "4 PM",
	 "", "", "", "8 PM","", "", "11 PM"])
	html = mpld3.fig_to_html(fig)
	#writes to our display file
	with open("html_plots/bike_changes.html", "w") as myfile:
		myfile.write(html)

