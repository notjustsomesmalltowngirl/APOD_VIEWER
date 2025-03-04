# Astronomy photo of the day viewer app
#### Video demo: [watch here](https://youtu.be/qrVX1r0xAKI)
## Description:
**Shows photos**: The Astronomy Photo of the Day Viewer App is a user-friendly application that fetches and displays the Astronomy Photo 
of the Day (APOD) using NASA’s API. I discovered this fascinating feature while exploring APIs to build my project with, and it quickly became an
inspiration for this project. The APOD often features stunning images (and occasionally videos), making it an exciting way 
to explore space from a really simple app. It also saves all the images gotten back into an "apod_images" directory in .png format.

**Explanation and title**: the api also returns a breif explanation of the photo returned and the title as well which are also 
displayed on the app.
## Features
**Help**: It contains an _instructions_ Button which explains how to use the app.

**Fetch Photos by Date**: Users can input any date and their API key to retrieve the APOD for that specific day.

**Favorite Photos**: Users can save their favorite photos, which are stored in a local favorites.txt file, allowing offline access.

**Navigation**: The app includes "Next" and "Previous" buttons to browse through different photos easily the right arrow and left arrow buttons 
also performs this function.

**Video Handling**: If the APOD is a video, a message box informs the user, as the app currently supports images only.

**Error handling**: If the user inputs a wrong api key, is not connected to the internet, or inputs a wrong date, a messagebox(from Tkinter)
informs the user.

**Offline access to favorites**: User can view the photos added to favorites using the see faves button or the Ctrl-f 
even when offline or after exiting the app cause the favorites are saved to a txt file "favorites.txt."

## Libraries used

**datetime**: This app uses the datetime module to check the validity of the user's input

**requests**: To get data from NASA's api.

**Pillow**: to convert the photo into a Tkinter displayable image.