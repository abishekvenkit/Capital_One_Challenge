# Capital_One_Challenge

Link To Web Application: https://capital-one-challenge-abishek.herokuapp.com/

This Repository implements a web application for the Capital One Winter Summit Coding Challenge. The purpose of the application
is to visualize bike share data from the Los Angeles area.

The web application was made using: <br>
  -Python Flask <br>
  -mpld3 <br>
  -Google Maps API <br>
  -Bootstrap
  
 Some other notes: The mpld3 library was used to create graphs for data visualization. The library exported interactive figures
 to html, which was then embedded into the web page. You can zoom into the graphs and scale them using the interactive buttons on the bottom left. The styling of the web page used CSS styling and a basic bootstrap template
 
 Important Files: <br>
 -graphs.py - holds the functions to create the plots <br>
 -app.py - runs the app <br>
 -templates files - html files for each page <br>
 -html_plots folder - holds the raw html for the plots created using matplotlib and mpld3
 
 NOTE: Some data was pulled from the online website https://bikeshare.metro.net/about/data/?. This was because some of the data
 for the season plots in the orginal csv did not seem sufficient.
