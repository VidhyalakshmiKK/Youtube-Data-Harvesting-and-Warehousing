# ========================================   /  Required Libraries   /   =================================== #

# Youtube API libraries
import googleapiclient.discovery
from googleapiclient.errors import HttpError

# SQL and Pandas libraries
import mysql.connector 
import pandas as pd
import isodate
import time

# Dash board libraries
import plotly.express as px
import streamlit as st

# ========================================   /   Dash board   /   =================================== #

# Configuring Streamlit GUI 

st.set_page_config(page_title="Youtube Data Harvesting and Warehousing", page_icon="https://upload.wikimedia.org/wikipedia/commons/7/75/YouTube_social_white_squircle_%282017%29.svg",
                   layout="wide", initial_sidebar_state="auto", menu_items=None)

# Title

st.title(":red[YouTube] :black[Data Harvesting and Warehousing 📈] ")

# Tabs 

tab1,tab2,tab3 = st.tabs([ "🖥️ HOME","🗃 DATA MIGRATION","📊 QUERYING"])

tab1.markdown("<h2 style='text-align: left;'> Hey Guyss !! </h2>", unsafe_allow_html=True)
tab1.markdown("##### :grey[This is Youtube Data Harvesting and Warehousing streamlit application allows you to access and analyze data from multiple YouTube channels.]")
tab1.image("D:/data science - guvi/MDT-34/capstone project/streamlit images/front.png")


# Sidebar

with st.sidebar:
   
   st.image("D:/data science - guvi/MDT-34/capstone project/streamlit images/YouTube-logo-with-shadow-PNG.png",use_column_width=True)
   
   st.markdown("#### :red[Domain] : :grey[Social Media]")
   st.markdown("#### :red[Skills take away from this Project] : :grey[Python scripting, Data Collection, Streamlit, API integration, Data Management using SQL]")
   st.markdown("#### :red[Overall view] : :grey[Building a simple UI with Streamlit, retrieving data using YouTube API, storing it in SQL database, querying the data warehouse with SQL, and displaying the output in the Streamlit application]")
   st.markdown("#### :red[Developed by] : :grey[VIDHYALAKSHMI K K]")


# ========================================   /   Data collection zone   /   =================================== #

#Connecting with Youtube API

api_key="AIzaSyBo-Ahr4FpvbTTYzfvuiUXF5IyB8Snk47M"
api_service_name = "youtube"
api_version = "v3"
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = api_key)


#Function to get channel details

def get_channel_details (channel_id):

    try:
        
        try:
            # Initialise a request to fetch channel details
            request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id = channel_id
            )
            response = request.execute()

            # Checking if the channel id is valid
            if 'items' not in response:
                        st.write(f"Invalid channel id: {channel_id}")
                        st.error("Enter the correct **channel_id**")
                        return None
            
            else:
                # Extract and format channel information
                channel_details={
                            'Channel_Name':response['items'][0]['snippet']['title'],
                            'Channel_Id':response['items'][0]['id'],
                            'Subscription_Count':response['items'][0]['statistics']['subscriberCount'],
                            'Channel_Views':response['items'][0]['statistics']['viewCount'],
                            'Channel_Description':response['items'][0]['snippet']['description'],
                            'Playlist_Id':response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                            }
                return channel_details
            
        except HttpError as e:
                    st.error('Server error (or) Check your internet connection (or) Please Try again after a few minutes', icon='🚨')
                    st.write('An error occurred: %s' % e)
                    return None
    except:
        
        st.write('You have exceeded your YouTube API quota. Please try again tomorrow.')


#Function to get Video details

def get_video_details(channel_id):
    # initialising an empty list to fetch the video ids from playlist id
    video_ids = []
    
    # Initialising an empty list to fetch the video details 
    video_details=[]

    # get Uploads playlist id
    channel_request = youtube.channels().list(id=channel_id,
                                               part='contentDetails')
    channel_response=channel_request.execute()
    playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    # get video ids from uploads playlist id
    while True:
        Playlist_items_request = youtube.playlistItems().list(playlistId=playlist_id,
                                                               part='snippet',
                                                               maxResults=50,
                                                               pageToken=next_page_token)
        Playlist_items_response = Playlist_items_request.execute()

        for i in range(len(Playlist_items_response['items'])):
            video_ids.append(Playlist_items_response['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = Playlist_items_response.get('nextPageToken')

        # Check if there are no more playlists in this channel
        if next_page_token is None:
            break

    # Initialise a request to fetch video details
    for i,item in enumerate(video_ids):
      Video_details_request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=item)
      Video_details_response = Video_details_request.execute()
     
      # conversion of duration to proper format (seconds)
      duration_str = Video_details_response['items'][0]['contentDetails']['duration']
      duration = isodate.parse_duration(duration_str)
      duration_sec = duration.total_seconds()

      if Video_details_response ['items']:
        video_info = {'Video_Id' : Video_details_response['items'][0]['id'],
                      'Channel_Id':Video_details_response['items'][0]['snippet']['channelId'],
                      'Playlist_Id': channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
                      'Video_name' : Video_details_response['items'][0]['snippet']['title'],
                      'Video_description' :Video_details_response['items'][0]['snippet'].get('description', ""),
                      'Tags' :Video_details_response['items'][0]['snippet'].get('tags',[]),
                      'Published_date' : Video_details_response['items'][0]['snippet']['publishedAt'][0:10],
                      'View_count' : Video_details_response['items'][0]['statistics'].get('viewCount', 0),
                      'Like_count' : Video_details_response['items'][0]['statistics'].get('likeCount', 0),
                      'Favorite_count' : Video_details_response['items'][0]['statistics']['favoriteCount'],
                      'Comment_count' : Video_details_response['items'][0]['statistics'].get('commentCount', 0),
                      'Duration' : duration_sec,
                      'Thumbnail' :  Video_details_response['items'][0]['snippet']['thumbnails']['default']['url'],
                      'Caption_status' : Video_details_response['items'][0]['contentDetails']['caption']
                      }
        
        if video_info['Tags'] == []:
            del video_info['Tags']
        if video_info['Caption_status'] == "false":
          video_info['Caption_status']="Not Available"
        else:
           video_info['Caption_status']="Available"
        if video_info['Video_description'] == "":
            video_info['Video_description'] = "Not Available"

        # appending info of each video to video_details list and returning it
        video_details.append(video_info)

    return video_details

#Function to get Comment details

def get_comment_details(channel_id): 

    # initialising an empty list to fetch the video ids from playlist id
    video_ids = []
    # initialising an empty list to fetch the comment details
    comment_details = []

    # get Uploads playlist id
    channel_request = youtube.channels().list(id=channel_id,part='contentDetails')
    channel_response=channel_request.execute()
    playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    # get video ids from uploads playlist id
    while True:
          Playlist_items_request = youtube.playlistItems().list(playlistId=playlist_id,
                                                               part='snippet',
                                                               maxResults=3,
                                                               pageToken=next_page_token)
          Playlist_items_response = Playlist_items_request.execute()

          for i in range(len(Playlist_items_response['items'])):
              video_ids.append(Playlist_items_response['items'][i]['snippet']['resourceId']['videoId'])
          next_page_token = Playlist_items_response.get('nextPageToken')
          
          # Check if there are no more playlists in this channel
          if next_page_token is None:
              break
    next_page_token = None

    
    for i,item in enumerate(video_ids):
        try:
            # Initialise a request to fetch comment details
            comment_details_request = youtube.commentThreads().list(
                part="snippet,replies",
              maxResults=100,
              pageToken=next_page_token,
              videoId=item)
            comment_details_response = comment_details_request.execute()

            for comment in comment_details_response['items']:
                
                comment_information = {"Comment_Id": comment['snippet']['topLevelComment'].get('id','Unavailable'),
                                     "Video_Id": comment['snippet']['videoId'],
                                     "Comment_Text": comment['snippet']['topLevelComment']['snippet'].get('textDisplay','Unavailable'),
                                     "Comment_Author": comment['snippet']['topLevelComment']['snippet'].get('authorDisplayName','Unavailable'),
                                     "Comment_Published_date": comment['snippet']['topLevelComment']['snippet']['publishedAt'][0:10],
                }
                
                comment_details.append(comment_information)
                next_page_token = comment_details_response.get('nextPageToken')
        
        except HttpError as e:
            if e.resp.status == 403 and b'commentsDisabled' in e.content:
                continue
                
            
    return comment_details

# ========================================   /   Data Migration to MySQL  /   =================================== #

# Connecting with MySQL database

conn = mysql.connector.connect(host='127.0.0.1',
                               user='root',
                               password='root',
                               database= 'Youtube_Data_Harvesting',
                               auth_plugin='mysql_native_password',
                               connection_timeout= 28800,
                               autocommit=True,
                               buffered=True
                              )
cursor = conn.cursor()

# Creating a new database if doesn't exist

cursor.execute("CREATE DATABASE IF NOT EXISTS Youtube_Data_Harvesting")

# Creating channel details table(if doesn't exist) and inserting values into the MySQL table

def channel_details_to_sql(channel_id):

     channel_details = """CREATE TABLE IF NOT EXISTS Channel_Details(Channel_Id VARCHAR(255) PRIMARY KEY,
							                                    Channel_Name VARCHAR(255),
                                                                Subscription_Count BIGINT,
                                                                Channel_Views BIGINT,
                                                                Channel_Description TEXT,
                                                                Playlist_Id VARCHAR(255));"""

     cursor.execute(channel_details)
     
     # Fetching the channel details and converting it into dataframe
     channel_details=get_channel_details(channel_id)
     channel_df = pd.DataFrame.from_dict(channel_details, orient='index').T
     try:
          conn.start_transaction()

          # Inserting values from dataframe into channel_details table in MySQL database 
          insert_query = """INSERT INTO channel_details (`Channel_Name`, `Channel_Id`, `Subscription_Count`, `Channel_Views`, `Channel_Description`, `Playlist_Id`)
              VALUES (%s, %s, %s, %s, %s, %s)"""
          for i in channel_df .to_dict("records"):
               cursor.execute(insert_query,(i['Channel_Name'],i['Channel_Id'],i['Subscription_Count'],i['Channel_Views'],i['Channel_Description'],i['Playlist_Id']))
          
           # creating streamlit progress bar
          for percent_complete in range(21,40):
              time.sleep(0.1)
              my_bar.progress(percent_complete + 1, text=progress_text)
          
     except Exception as e:
         if 'Duplicate entry' in str(e):
            my_bar.empty()
            tab2.warning('Duplicate entry of channel id', icon="⚠️")
            tab2.write(" This channel data has already been uploaded to the database")
         else:
            tab2.error(e) 
            conn.rollback()

# Creating video details table(if doesn't exist) and inserting values into the table

def Video_details_to_sql(channel_id):

    video_details="""CREATE TABLE IF NOT EXISTS Video_Details(Video_Id VARCHAR(255) PRIMARY KEY,
						                                  Channel_Id VARCHAR(255),
                                                          Playlist_Id VARCHAR(255),
                                                          Video_name VARCHAR(255), 
                                                          Video_description TEXT,
                                                          Published_date DATE,
                                                          View_count BIGINT,
                                                          Like_count BIGINT,
                                                          Favorite_count INT,
                                                          Comment_count INT,
                                                          Duration INT,
                                                          Thumbnail VARCHAR(255),
                                                          Caption_status VARCHAR(255),
                                                          FOREIGN KEY (Channel_Id) REFERENCES Channel_Details(Channel_Id));"""

    cursor.execute(video_details)

    # Fetching the video details and converting it into dataframe
    video_details=get_video_details(channel_id)
    video_df = pd.DataFrame(video_details)

    try:
          # Inserting values from dataframe into video_details table in MySQL database 
          insert_query = """INSERT INTO video_details (`Video_Id`,`Channel_Id` ,`Playlist_Id`, `Video_name`, `Video_description`, `Published_date`, `View_count`, `Like_count`, `Favorite_count`, `Comment_count`, `Duration`, `Thumbnail`, `Caption_status`)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
          for i in video_df .to_dict("records"):
               cursor.execute(insert_query,(i['Video_Id'],i['Channel_Id'],i['Playlist_Id'],i['Video_name'],i['Video_description'],i['Published_date'],i['View_count'],i['Like_count'],i['Favorite_count'],i['Comment_count'],i['Duration'],i['Thumbnail'],i['Caption_status']))
          
          # creating streamlit progress bar
          for percent_complete in range(40,70):
              time.sleep(0.1)
              my_bar.progress(percent_complete + 1, text=progress_text)
          
    except Exception as e:
         if 'Duplicate entry' in str(e):
            pass
         else:
            tab2.error( e)#"An error occurred:",
            conn.rollback()
            
# Function to Create comment details table(if doesn't exist) and to insert values into the table

def Comment_details_to_sql(channel_id):

    comment_details="""CREATE TABLE IF NOT EXISTS Comment_Details(Comment_Id VARCHAR(255) PRIMARY KEY,
                                                              Video_Id VARCHAR(255),
                                                              Comment_Text TEXT,
                                                              comment_Author VARCHAR(255),
                                                              Comment_Published_date DATE,
                                                              FOREIGN KEY (Video_Id) REFERENCES Video_Details(Video_Id));"""

    cursor.execute(comment_details)
    conn.commit()

    # Fetching the channel details and converting it into dataframe
    comment_details=get_comment_details(channel_id)
    comments_df = pd.DataFrame(comment_details)

    try:
         # Inserting values from dataframe into comment_details table in MySQL database 
         insert_query = """INSERT INTO comment_details (`Video_Id`, `Comment_Id`, `Comment_Text`, `Comment_Author`, `Comment_Published_date`)
              VALUES (%s, %s, %s, %s, %s)"""

         for i in comments_df .to_dict("records"):
              cursor.execute(insert_query,(i['Video_Id'],i['Comment_Id'],i['Comment_Text'],i['Comment_Author'],i['Comment_Published_date']))
         conn.commit()

         # creating streamlit progress bar
         for percent_complete in range(70,100):
              time.sleep(0.1)
              my_bar.progress(percent_complete + 1, text=progress_text)
         my_bar.empty()
        
        
         with st.spinner('Please wait '):
             time.sleep(5)
             tab2.success('Done!! Data Uploaded Successfully')
             tab2.snow()  
         
    except Exception as e:
         if 'Duplicate entry' in str(e):
            pass
         else:
            tab2.error(e)#"An error occurred:",
            conn.rollback()
            my_bar.empty()

# Function to call other functions to create tables and insert values to MySQL

def tables(channel_id):
    channel_details_to_sql(channel_id)
    Video_details_to_sql(channel_id)
    Comment_details_to_sql(channel_id)

# Creating the streamlit page for Data Migration Zone

tab2.header(":grey[Data Migration zone]")
tab2.image("D:/data science - guvi/MDT-34/capstone project/streamlit images/data analysis _3.png", use_column_width=True) 
tab2.subheader(":grey[Inserting Data into] :blue[MySQL] :grey[database for Analysis] ⌛")
tab2.write("(**Note**: This zone **collects the data** by using channel id and **store it in the :blue[MySQL] database**.)")
channel_id = tab2.text_input("Enter the channel Id") # getting channel id as input from user



tab2.subheader(":grey[Fetching Channel Data ]")
tab2.write('''(**Note**: To fetch the data and store it in the MySQL database click below **:blue['Upload data into MySQL']**.)''')
submit = tab2.button("**Upload data into :blue[MySQL]**") # creating a buuton for data collection and migration

if submit:

    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(1,20):
        time.sleep(0.1)
        my_bar.progress(percent_complete + 1, text=progress_text)
    tables(channel_id) #calling  function tables to collect data and insert into MySQL   

# ========================================   /   Data Querying zone   /   =================================== #

tab3.header(':grey[Channel Data Analysis zone]')
tab3.write ('''(Note:- :red[**Analysis of channel data**] depends on your selected question and gives an output in a table format)''')

#Creating a dropdown list box to select the required question to analyse the data

questions = tab3.selectbox("Select any questions given below:",
['1. What are the names of all the videos and their corresponding channels?',
'2. Which channels have the most number of videos, and how many videos do they have?',
'3. What are the top 10 most viewed videos and their respective channels?',
'4. How many comments were made on each video, and what are their corresponding video names?',
'5. Which videos have the highest number of likes, and what are their corresponding channel names?',
'6. What is the total number of likes for each video, and what are their corresponding video names?',
'7. What is the total number of views for each channel, and what are their corresponding channel names?',
'8. What are the names of all the channels that have published videos in the year 2022?',
'9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
'10. Which videos have the highest number of comments, and what are their corresponding channel names?'])


# Queries to be stored in Variables:
 
if questions == '1. What are the names of all the videos and their corresponding channels?':
    query1 = "SELECT ch.Channel_Name , v.Video_name FROM video_details v LEFT JOIN channel_details ch ON ch.Channel_Id = v.Channel_Id ;"
    cursor.execute(query1)

    #Storing the results in Pandas Dataframe:
    df1 = pd.DataFrame(cursor.fetchall(),columns = ['Channel Name', 'Name of the Video']).reset_index(drop=True)
    df1.index = df1.index+1
    tab3.dataframe(df1)

elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
   
   col1,col2 = st.columns(2)
   # Storing the results in Pandas Dataframe
   with col1: 
      query2 = "SELECT ch.Channel_Name,COUNT(v.Video_Id) AS Video_Count FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id  = v.Channel_Id GROUP BY ch.Channel_Name ORDER BY Video_Count desc ;"
      cursor.execute(query2)
      df2 = pd.DataFrame(cursor.fetchall(),columns = ['Channel Name','Video Count']).reset_index(drop=True)
      df2.index = df2.index+1
      tab3.dataframe(df2)
   # creating a bar chart for the output
   with col2:
      fig1 = px.bar(df2, y='Video Count', x='Channel Name', text_auto='.2s', title='Channel with most number of Videos',color='Video Count',color_continuous_scale='teal',hover_data={'Video Count': True} )
      fig1.update_traces(textfont_size=16,marker=dict(line=dict(width=1, color='DarkSlateGrey')))
      fig1.update_layout(title_font_color='#616569',title_font=dict(size=25),coloraxis_showscale=True)
      tab3.plotly_chart(fig1,use_container_width=True)
      

elif questions == '3. What are the top 10 most viewed videos and their respective channels?':

   col1,col2 = st.columns(2)
   # Storing the results in Pandas Dataframe
   with col1:
      query3 = "SELECT ch.Channel_Name , v.Video_name , v.View_count FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id  = v.Channel_Id  ORDER BY v.View_count DESC LIMIT 10;"
      cursor.execute(query3)
      df3 = pd.DataFrame(cursor.fetchall(),columns=['Channel Name','Video Name','View Count']).reset_index(drop=True)
      df3.index = df3.index+1
      tab3.dataframe(df3)
      # creating a pie chart for the output
   with col2:
      fig2 = px.pie(df3, values='View Count', names='Video Name', title='Top 10 most viewed videos',hole=0.4, color_discrete_sequence = px.colors.sequential.Teal,hover_data={'Channel Name':True,'Video Name':True,'View Count': True} )
      fig2.update_traces(textfont_size=16,marker=dict(line=dict(width=1, color='DarkSlateGrey')))
      fig2.update_layout(title_font_color='#616569',title_font=dict(size=25),coloraxis_showscale=True)
      tab3.plotly_chart(fig2,use_container_width=True)
       
   

elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
   
   col1,col2 = st.columns(2)
   with col1:
      # Storing the results in Pandas Dataframe
      query4 = "SELECT  ch.Channel_Name , v.Video_name , v.Comment_count FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id  = v.Channel_Id  ORDER BY Comment_count DESC ;"
      cursor.execute(query4)
      df4 = pd.DataFrame(cursor.fetchall(),columns=['Channel Name','Name of the Video','No of Comments']).reset_index(drop=True)
      df4.index = df4.index+1
      tab3.dataframe(df4)
   with col2:
      # creating a pie chart for the output
      query_4 = "SELECT  ch.Channel_Name , v.Video_name , v.Comment_count FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id  = v.Channel_Id  ORDER BY Comment_count DESC LIMIT 10;"
      cursor.execute(query_4)
      result=cursor.fetchall()
      df_4 = pd.DataFrame(result,columns=['Channel Name','Video Name','Comment Count']).reset_index(drop=True)
      fig_4 = px.pie(df_4, values='Comment Count', names='Video Name', title='Top 10 most Commented Videos',hole=0.4, color_discrete_sequence = px.colors.sequential.Teal,hover_data=['Channel Name','Video Name','Comment Count'] )
      fig_4.update_traces(textfont_size=14,marker=dict(line=dict(width=1, color='DarkSlateGrey')))
      fig_4.update_layout(title_font_color='#616569',title_font=dict(size=25),coloraxis_showscale=True)
      tab3.plotly_chart(fig_4,use_container_width=True)
    

elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
   col1,col2 = st.columns(2)
   with col1:
      # Storing the results in Pandas Dataframe
      query5 = "SELECT ch.Channel_Name , v.Video_name AS Name_of_the_Video, v.Like_count AS No_of_Likes FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id = v.Channel_Id ORDER BY v.Like_count desc ;"
      cursor.execute(query5)
      df5 = pd.DataFrame(cursor.fetchall(),columns=['Channel Name','Name of the Video','No of Likes']).reset_index(drop=True)
      df5.index = df5.index+1
      tab3.dataframe(df5)
   with col2:
      # creating a pie chart for the output
      query_5 = "SELECT ch.Channel_Name , v.Video_name AS Name_of_the_Video, v.Like_count AS No_of_Likes FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id = v.Channel_Id ORDER BY v.Like_count desc LIMIT 10;"
      cursor.execute(query_5)
      df_5 = pd.DataFrame(cursor.fetchall(),columns=['Channel Name','Name of the Video','No of Likes']).reset_index(drop=True)
      fig_4 = px.pie(df_5, values='No of Likes', names='Name of the Video', title='Top 10 most Liked Videos',hole=0.4, color_discrete_sequence = px.colors.sequential.Teal,hover_data=['Channel Name','Name of the Video','No of Likes'] )
      fig_4.update_traces(textfont_size=14,marker=dict(line=dict(width=1, color='DarkSlateGrey')))
      fig_4.update_layout(title_font_color='#616569',title_font=dict(size=25),coloraxis_showscale=True)
      tab3.plotly_chart(fig_4,use_container_width=True)
    

elif questions == '6. What is the total number of likes for each video, and what are their corresponding video names?':
    # Storing the results in Pandas Dataframe
    query6 = "SELECT ch.Channel_Name , v.Video_name AS Name_of_the_Video, v.Like_count AS No_of_Likes FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id = v.Channel_Id ORDER BY v.Like_count desc ;"
    cursor.execute(query6)
    df6 = pd.DataFrame(cursor.fetchall(),columns=['Channel Name','Name of the Video','No of Likes']).reset_index(drop=True)
    df6.index = df6.index+1
    tab3.dataframe(df6)

elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
   col1, col2 = st.columns(2)
   with col1:
      # Storing the results in Pandas Dataframe
      query7 = "SELECT  Channel_Name , Channel_Views FROM Channel_Details ORDER BY Channel_Views DESC ;"
      cursor.execute(query7)
      df7 = pd.DataFrame(cursor.fetchall(),columns=['Channel Name','Total number of views']).reset_index(drop=True)
      df7.index = df7.index+1
      tab3.dataframe(df7)

      # creating a bar chart for the output
   with col2:
      fig3 = px.bar(df7, y='Total number of views', x='Channel Name', text_auto='.2s', title="Total number of views",color='Total number of views',color_continuous_scale='teal',hover_data= {'Channel Name':True,'Total number of views': True})
      fig3.update_traces(textfont_size=16,marker=dict(line=dict(width=1, color='DarkSlateGrey')))
      fig3.update_layout(title_font_color='#616569',title_font=dict(size=25))
      tab3.plotly_chart(fig3,use_container_width=True)
      

elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
    # Storing the results in Pandas Dataframe
    query8 = "SELECT DISTINCT ch.Channel_Name FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id = v.Channel_Id WHERE year(Published_date) = 2022 ;"
    cursor.execute(query8)
    df8 = pd.DataFrame(cursor.fetchall(),columns=['Channels published videos in 2022']).reset_index(drop=True)
    df8.index = df8.index+1
    tab3.dataframe(df8)


elif questions =='9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
   col1, col2 = st.columns(2)
   with col1:
      # Storing the results in Pandas Dataframe
      query9 = "SELECT ch.Channel_Name, TIME_FORMAT(SEC_TO_TIME(AVG(v.Duration)),'%H:%i:%s') AS Average_Duration_of_Videos FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id  = v.Channel_Id GROUP BY ch.Channel_Name ORDER BY Average_Duration_of_Videos ASC  ;"
      cursor.execute(query9)
      df9= pd.DataFrame(cursor.fetchall(),columns=['Channel Name','Average Duration of Videos']).reset_index(drop=True)
      df9.index += 1
      tab3.dataframe(df9)

   with col2:
      # creating a bar chart for the output
      fig4 = px.bar(df9, y='Channel Name',x='Average Duration of Videos', title='Average Duration of Videos', color='Average Duration of Videos',color_continuous_scale='teal',hover_data= {'Channel Name':True,'Average Duration of Videos': True})
      fig4.update_traces(textfont_size=16,marker=dict(line=dict(width=1, color='DarkSlateGrey')))
      fig4.update_layout(title_font_color='#616569',title_font=dict(size=25))
      tab3.plotly_chart(fig4,use_container_width=True)
   

elif questions =='10. Which videos have the highest number of comments, and what are their corresponding channel names?':
   col1, col2 = st.columns(2)
   with col1:
      # Storing the results in Pandas Dataframe
      query10 = "SELECT  ch.Channel_Name , v.Video_name AS Name_of_the_Video , v.Comment_count AS No_of_Comments FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id = v.Channel_Id ORDER BY Comment_count DESC ;"
      cursor.execute(query10)
      df10 = pd.DataFrame(cursor.fetchall(),columns=['Channel Name','Name of the Video','No of Comments']).reset_index(drop=True)
      df10.index += 1
      tab3.dataframe(df10)
   with col2:
      # creating a pie chart for the output
      query_10 = "SELECT  ch.Channel_Name , v.Video_name AS Name_of_the_Video , v.Comment_count AS No_of_Comments FROM Video_Details v LEFT JOIN Channel_Details ch ON ch.Channel_Id = v.Channel_Id ORDER BY Comment_count DESC limit 20 ;"
      cursor.execute(query_10)
      df_10 = pd.DataFrame(cursor.fetchall(),columns=['Channel Name','Name of the Video','No of Comments']).reset_index(drop=True)
      fig5 = px.pie(df_10, values='No of Comments', names='Name of the Video', title="Top 20 Videos with highest number of comments",hole=0.4, color_discrete_sequence = px.colors.sequential.Teal,hover_data=['Channel Name','Name of the Video','No of Comments'])
      fig5.update_traces(textfont_size=16,marker=dict(line=dict(width=1, color='DarkSlateGrey')))
      fig5.update_layout(title_font_color='#616569',title_font=dict(size=25))
      tab3.plotly_chart(fig5,use_container_width=True)

# Closing SQL database connection
conn.close()

# ========================================   /   End  /   ========================================  #