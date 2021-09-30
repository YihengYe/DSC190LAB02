# Internet of Things--Visualization of San Diego Micro-climate And Local Wind Speed Prediction

Final website: http://dsc-iot.ucsd.edu/gid03/index.html


In our project, we used DHT sensor data from all teams to model and predict the wind speed by temperature and humidity.

Users could interact freely with several embedded functions. Firstly, users could change the red circle’s radius to selectively include the sensors and display the data accordingly across different charts.

When the users move the mouse over a marker, a window will pop up with the latest average temperature and humidity by each day. When the users click on the marker, a side navigation bar will show on the right side, displaying all different kinds of analysis. In the side bar, we plotted the humidity versus temperature line chart and also included the predicted weed speed in the chart. The wind speed is calculated in the notebook named “wind_speed_predicton”. Since the server hosted by DSC-IOT does not support various python package, a linear regressor is trained on the weather data in the server. We use temperature, humidity, as features and window as labels and found such a relationship among those three variables: -0.3539*temp-0.0713*hum+19.6735 = wind speed. The line chart is interactable. The users could drag, zoom in or out to selector a specified period of time and watch the data closely. 

Below the side bar, we also have a scatter plot that visualize the correlation between temperature and humidity. We found a slightly negative correlation exists between temperature and humidity.  The scatter plot is interactable too. As the circle increases its radius, more and more data are included in the scatter plots. We could spot a clear negative trend then.

The side bar could be close by clicking on “Close Sidebar”.

