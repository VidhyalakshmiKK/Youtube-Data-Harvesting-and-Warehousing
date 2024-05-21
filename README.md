# Youtube Data Harvesting and Warehousing using SQL and streamlit
## Introduction
The YouTube Data Harvesting and Warehousing project aims to create an intuitive Streamlit application that leverages the power of the Google API to extract data from YouTube channels. This data is transferred to a MySQL data warehouse using user-friendly Streamlit interface.

## Table of Contents
   1.Key Technologies and Skills

   2.Usage
   
   3.Features
   
   4.Explanation of the code
   
   5.Contact Information
   
## Key Technologies and Skills
   • Python Scripting
   
   • Data Collection
   
   • API Integration
   
   • Streamlit
   
   • Data Management using MySQL

## Usage
To use this project, follow these steps:

  1.Install the required packages
  
  2.Run the Streamlit app: streamlit run app.py
  
  3.Open the app in your web browser. You can access it by opening a new tab and entering the following URL: http://192.168.0.103:8501
  
## Features
  • Retrieve data from the YouTube API, including channel information, playlists, videos, and comment details.
  
  • Store the collected data in MySQL data warehouse.
  
  • Analyze and visualize data using Streamlit and other Python libraries.
  
  • Perform queries on the MySQL data warehouse.
  
  • Answer default 10 queries to provide immediate insights into the data.

## Explanation of the code
The provided code is a Python script that uses the Streamlit library to create a web application for fetching data from the YouTube API,storing it in a MySQL database for further analysis. Here's a brief explanation of the code:

• The script imports necessary libraries and modules, including Streamlit, Google API client, time, pandas, plotly.express and mysql.connector.

• It sets the Streamlit page configuration and displays a title for the web application.

• The code defines several functions for fetching data from the YouTube API, including channel details, video details and comment details. These functions use the provided YouTube API key to make API requests and retrieve the desired data.

• The code defines several functions to create MySQL tables and store the retrieved data those tables.

• The code checks for user input (channel ID) and a button click to fetch channel details and upload them to the MySQL database.It calls the previously defined functions to fetch channel details video details, and comment details.The fetched data is then inserted into the corresponding tables in MySQL database. It uses pandas and the mysql.connector for the data insertion process.

• Finally, the script provides a selection box for the user to choose from several predefined questions. Based on the selected question, the script executes
corresponding SQL queries on the MySQL database and retrieves the results. The results are displayed in a table using Streamlit's dataframe and bar chart or pie charts are displayed for necessary quesries using plotly.express

Overall, the code combines the functionalities of fetching data from the YouTube API, storing it in MySQL, and displaying the results in a web application using Streamlit.

## Contact Information
Email: kkvidhyalakshmi@gmail.com 

