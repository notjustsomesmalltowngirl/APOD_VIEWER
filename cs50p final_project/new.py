import requests
import re
import os
from datetime import datetime
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO
from tkinter import messagebox

BACKGROUND_COLOR = "#4A628A"
CANVAS_COLOR = "#CBDCEB"
BUTTON_COLOR = '#9B7EBD'
CANVAS_HEIGHT = 600
CANVAS_WIDTH = 600
TITLE_FONT = ('Arial', 14, 'bold')
EXPLANATION_FONT = ('poppins', 12, 'italic')


def date_is_valid(input_date: str) -> bool:
    try:
        datetime.strptime(input_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


apod_images = []
CURRENT_INDEX = 0


def get_apod(event=None):
    """gets astronomy pictures of whatever date you put in"""
    global CURRENT_INDEX
    date = date_entry.get()
    api_key = api_entry.get()
    # check if the user has filled both date and api key fields
    if not date or not api_key:
        messagebox.showinfo(title='Empty Fields',
                            message='Please fill both API and date fields'
                            )
        return None
    # check if the user inputted a valid date
    if not date_is_valid(date):
        messagebox.showinfo(title='Invalid date',
                            message='Please input a valid date in (YYYY-MM-DD) format'
                            )
        return None
    parameters = {
        'date': date,
        'api_key': api_key,
    }
    # try to get the apod data from NASA's API
    try:
        response = requests.get(f'https://api.nasa.gov/planetary/apod',
                                params=parameters
                                )
        response.raise_for_status()
        apod_data = response.json()

    except requests.exceptions.HTTPError:
        if response.status_code == 400:
            try:
                error_msg = response.json()['msg']
            # except the error dictionary doesn't have a 'msg' key
            except KeyError:
                error_msg = 'An error occurred'
            messagebox.showinfo(title=f'{response.status_code} Client error', message=error_msg)

        elif re.search(r'^40[1-5]$', str(response.status_code)):
            messagebox.showinfo(title='API Key Error',
                                message='Invalid or missing API key. Please check your API key.'
                                )
        return None
    except requests.exceptions.RequestException:
        messagebox.showinfo(title='Request Error',
                            message='An error occurred while fetching data'
                                    'Check your connection and try again later'
                            )
        return None
    if 'url' in apod_data and apod_data['media_type'] == 'image':
        # get the image url from data returned from NASA's API
        image_url = apod_data['url']
        image_response = requests.get(image_url)
        # get the image data
        image = Image.open(BytesIO(image_response.content))
        # save images into apod_images directory
        folder_path = 'apod_images'
        os.makedirs(folder_path, exist_ok=True)
        filename = f'apo_{date}.png'
        file_path = os.path.join(folder_path, filename)
        image.save(file_path)
        # add all the images to a list
        apod_images.append((file_path, apod_data['title'], apod_data['explanation']))
        CURRENT_INDEX = len(apod_images) - 1  # so it never goes out of range

        return apod_images[CURRENT_INDEX]

    messagebox.showinfo(title="No Image",
                        message="No image available for the selected date."
                        )
    return None


IMAGE_TO_DISPLAY = None
image_path = ''


def display_photo_on_canvas(event=None):
    global IMAGE_TO_DISPLAY, image_path
    if apod_images:
        image_path, title, explanation = apod_images[CURRENT_INDEX]

        image = Image.open(image_path)
        image = image.resize((600, 600), Image.Resampling.LANCZOS)
        IMAGE_TO_DISPLAY = ImageTk.PhotoImage(image)
        canvas.itemconfig(canvas_bg, image=IMAGE_TO_DISPLAY)
        canvas.itemconfig(title_text, text=title)
        canvas.itemconfig(explanation_text, text=explanation)
        # when the user asks to get 'photo' make the button to get faves available
        get_previous.config(state=NORMAL if CURRENT_INDEX > 0 else DISABLED)
        add_to_faves.config(state=NORMAL)
        get_next.config(state=NORMAL if CURRENT_INDEX < len(apod_images) - 1 else DISABLED)
        date_entry.delete(0, END)


def show_previous_image(event=None):
    global CURRENT_INDEX
    #  check if we have more than one photo recall that 'current index' is the number of images - 1
    if CURRENT_INDEX > 0:
        CURRENT_INDEX -= 1  # reduce 'current index' by one each time function is called
        display_photo_on_canvas()  # then display that previous photo on canvas


def show_next_image(event=None):
    global CURRENT_INDEX
    # check if the user has clicked the previous button
    if CURRENT_INDEX < len(apod_images) - 1:
        CURRENT_INDEX += 1  # if True, increase the index by one till we reach 'current picture'
        display_photo_on_canvas()


FAV_FILE = 'favorites.txt'


def add_faves_to_file(event=None):
    global image_path
    with open(FAV_FILE, mode='a+') as file:
        file.seek(0)
        existing_faves = file.read().strip()
        if image_path not in existing_faves:
            file.write(f"{image_path}\n")
            messagebox.showinfo(message='Added to favorites.')
        else:
            messagebox.showinfo(message='Already in Favorites.')


index = -1


def show_faves(event=None):
    global image_path, index
    with open(FAV_FILE) as file:
        list_of_faves = file.read().splitlines()  # read the lines of the file as a list
        #  add one to index so each time the button that calls this function is called the index increases by 1
        index = (index + 1) % len(list_of_faves)  # using % so it doesn't go over the number of items in the list
        image_path = list_of_faves[index].strip()  # get the image_path that corresponds to the index
        image = Image.open(image_path)  # open the image
        image = image.resize((CANVAS_WIDTH, CANVAS_HEIGHT))  # resize the image accordingly
        photo = ImageTk.PhotoImage(image)
        date = re.sub(r'[a-z_.\\]', '', image_path, )
        canvas.itemconfig(title_text, text=f'Favorite {date}')
        canvas.itemconfig(explanation_text, text='')
        canvas.itemconfig(canvas_bg, image=photo)
        canvas.image = photo  # save image so it doesn't get garbage collected


def file_is_empty():
    with open(FAV_FILE, mode='r') as file:
        return file.read().strip() == ''


def get_photo(event=None):
    # calls lambda: (get_apod(), display_photo_on_canvas())
    get_apod()
    display_photo_on_canvas()


root = Tk()
root.geometry('600x700')
root.resizable(width=False, height=False)
root.title("Astronomy picture of the day")

bg_image = Image.open('label_bg_imagee.jpg')
bg_image = bg_image.resize((700, 700))
bg_photo = ImageTk.PhotoImage(bg_image)
background_label = Label(root, image=bg_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

api_label = Label(text="Enter API key", bg=BUTTON_COLOR, width=16)
api_label.grid(row=1, column=0, pady=5)

api_entry = Entry(width=50, bg=BUTTON_COLOR)
api_entry.grid(row=1, column=1)
api_entry.focus()

date_label = Label(text="Date(YYYY-MM-DD)", bg=BUTTON_COLOR)
date_label.grid(row=2, column=0, pady=5)

date_entry = Entry(width=50, bg=BUTTON_COLOR)
date_entry.grid(row=2, column=1)

get_previous = Button(text='⬅️ Previous', bg=BUTTON_COLOR, command=show_previous_image)
get_previous.config(state=DISABLED)
get_previous.place(x=290, y=667)
root.bind('<Left>', show_previous_image)
get_photo_button = Button(text='Get Photo', bg=BUTTON_COLOR,
                          command=lambda: (get_apod(), display_photo_on_canvas()))
get_photo_button.place(x=390, y=667)
root.bind('<Return>', get_photo)
get_next = Button(text='Next ➡️', bg=BUTTON_COLOR, command=show_next_image)
get_next.config(state=DISABLED)
get_next.place(x=480, y=667, width=60)
root.bind('<Right>', show_next_image)

add_to_faves = Button(
    text='❤Add to faves⭐', bg=BUTTON_COLOR,
    command=add_faves_to_file
)
add_to_faves.config(state=DISABLED)
add_to_faves.place(x=80, y=667)
root.bind('<Control-f>', add_faves_to_file)

show_favorite_button = Button(text='See Faves', bg=BUTTON_COLOR, command=show_faves)
show_favorite_button.place_forget() if file_is_empty() else show_favorite_button.place(x=3, y=667)
root.bind('<Control-d>', show_faves)
canvas = Canvas(width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=CANVAS_COLOR, highlightthickness=0)
a_bg_img = ImageTk.PhotoImage(file='canvas_bg_image.jpg')
canvas_bg = canvas.create_image(300, 300, image=a_bg_img)

title_text = canvas.create_text(300, 20, text='', font=TITLE_FONT, fill='white')
explanation_text = canvas.create_text(300, 440, text='', font=EXPLANATION_FONT, fill='white',
                                      width=580)

canvas.grid(column=0, row=0, columnspan=2)

root.mainloop()
