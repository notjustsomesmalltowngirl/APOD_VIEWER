import requests
import re
import os
from datetime import datetime
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO
from tkinter import messagebox, filedialog
# from do
BACKGROUND_COLOR = "#4A628A"
CANVAS_COLOR = "#CBDCEB"
BUTTON_COLOR = '#9B7EBD'
CANVAS_HEIGHT = 600
CANVAS_WIDTH = 600
index = -1
IMAGE_TO_DISPLAY = None
image_path = ''
FAV_FILE = 'starred.txt'
apod_pack = []
CURRENT_INDEX = 0
NASA_URL_ENDPOINT = 'https://api.nasa.gov/planetary/apod'

def show_instructions(event=None):
    instructions_window = Toplevel(root)
    instructions_window.title("Using the APOD viewer App")
    instructions_window.geometry("400x350")
    instructions_window.configure(bg=BACKGROUND_COLOR)

    instructions_text = (
        "Welcome to the Astronomy Picture of the Day (APOD) Viewer!\n\n"
        "Instructions:\n"
        "- Enter a valid API key(You can get this from https://api.nasa.gov/) and a date in YYYY-MM-DD format.\n"
        "- Press 'Get Photo' to retrieve the image for the specified date.\n"
        "- Use the '❤ Star ⭐' button to save the image to your starred.\n"
        "- View your starred by pressing 'See starred' or pressing Ctrl + D.\n"
        "- Get previous and Next images with the ⬅️ and ➡️ buttons or Left/Right arrows.\n\n"
        "ShortCuts:\n"
        "- Enter: To Get Photo\n"
        "- Ctrl + F: Add an APOD to starred\n"
        "- Ctrl + D: View starred\n"
        "-Ctrl + i:  View instructions😉"
    )

    label = Label(instructions_window, text=instructions_text, bg=BACKGROUND_COLOR, fg="white", wraplength=380)
    label.pack(padx=10, pady=10)

    close_button = Button(instructions_window, text="Close", command=instructions_window.destroy, bg=BUTTON_COLOR)
    close_button.pack(pady=10)

    instructions_window.grab_set()


def date_is_valid(input_date: str) -> bool:
    try:
        datetime.strptime(input_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_apod(event=None):
    """gets astronomy pictures of whatever date you put in"""
    global CURRENT_INDEX
    date = date_entry.get()
    api_key = api_entry.get()
    # check if the user has filled both date and api key fields
    if not date or not api_key:
        messagebox.showwarning(
            title='Empty Fields',
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
        response = requests.get(NASA_URL_ENDPOINT,
                                params=parameters
                                )
        response.raise_for_status()
        apod_data = response.json()
        date_entry.delete(0, END)

    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            messagebox.showerror(
                title='API Key Error',
                message='Invalid or missing API key. Please check your API key.'
            )
            return None
        elif response.status_code != 200:
            # except the error dictionary doesn't have a 'msg' key
            error_msg = response.json().get('msg', 'An error occurred')
            messagebox.showerror(title=f'{response.status_code} Client error', message=error_msg)
            return None

        messagebox.showerror(
            title='HTTPError',
            message=f'An HTTPError occurred\n{e}'
        )
        return None
    except requests.exceptions.RequestException:
        messagebox.showerror(title='Request Error',
                             message='An error occurred while fetching data '
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
        apod_pack.append((file_path, apod_data['title'], apod_data['explanation']))
        CURRENT_INDEX = len(apod_pack) - 1  # so it never goes out of range

        return apod_pack[CURRENT_INDEX]

    messagebox.showinfo(title="No Image",
                        message="No image available for the selected date."
                        )
    return None


def display_photo_on_canvas(event=None):
    global IMAGE_TO_DISPLAY, image_path
    if apod_pack:
        image_path, title, explanation = apod_pack[CURRENT_INDEX]

        image = Image.open(image_path)
        image = image.resize((600, 600), Image.Resampling.LANCZOS)
        IMAGE_TO_DISPLAY = ImageTk.PhotoImage(image)
        update_canvas(canvas, IMAGE_TO_DISPLAY, explanation, title)
        update_buttons()

def update_canvas(canvas, image, explanation, title):
    canvas.itemconfig(canvas_bg, image=image)
    canvas.itemconfig(title_text, text=title)
    canvas.itemconfig(explanation_text, text=explanation)
    canvas.itemconfig(intro_text, text='')


def update_buttons():
    get_previous.config(state=NORMAL if CURRENT_INDEX > 0 else DISABLED)
    add_to_starred.config(state=NORMAL)
    get_next.config(state=NORMAL if CURRENT_INDEX < len(apod_pack) - 1 else DISABLED)


def show_previous_image(event=None):
    global CURRENT_INDEX
    #  check if we have more than one photo recall that 'current index' is the number of images - 1
    if CURRENT_INDEX > 0:
        CURRENT_INDEX -= 1  # reduce 'current index' by one each time function is called
        display_photo_on_canvas()  # then display that previous photo on canvas


def show_next_image(event=None):
    global CURRENT_INDEX
    # check if the user has clicked the previous button
    if CURRENT_INDEX < len(apod_pack) - 1:
        CURRENT_INDEX += 1  # if True, increase the index by one till we reach 'current picture'
        display_photo_on_canvas()


def add_starred_to_file(event=None):
    global image_path
    with open(FAV_FILE, mode='a+') as file:
        file.seek(0)
        existing_starred = file.read().strip()
        if image_path not in existing_starred:
            file.write(f"{image_path}\n")
            messagebox.showinfo(message='Added to starred.')
        else:
            messagebox.showinfo(message='Already in Starred.')


def show_starred(event=None):
    global image_path, index
    with open(FAV_FILE) as file:
        list_of_starred = [line.strip() for line in file if line.strip()]
        try:
            index = (index + 1) % len(list_of_starred)  # using % so it doesn't go over the number of items in the list
        except ZeroDivisionError:
            messagebox.showerror(title='Empty starred', message='No image in starred')
        else:
            image_path = list_of_starred[index].strip()  # get the image_path that corresponds to the index
            image = Image.open(image_path)  # open the image
            image = image.resize((CANVAS_WIDTH, CANVAS_HEIGHT))  # resize the image accordingly
            starred_photo = ImageTk.PhotoImage(image)
            date = re.sub(r'[a-z_.\\]', '', image_path, )
            update_canvas(canvas, starred_photo, '', f'starred {date}')
            canvas.image = starred_photo  # save image so it doesn't get garbage collected


def save_apod():
    try:
        pil_img = Image.open(image_path).convert('RGBA')
        save_path = filedialog.asksaveasfilename(
            title='Save Image: ', defaultextension='.png',
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )
        if save_path:
            try:
                pil_img.save(save_path)
                messagebox.showinfo('Image saved', f'Image saved successfully to {save_path}')
            except Exception as e:
                messagebox.showerror('Error', f'Error saving Image: {e}')
    except FileNotFoundError:
        messagebox.showerror('Error', 'Please fetch a photo or choose one from your starred list before saving.')


def get_photo(event=None):
    # calls lambda: (get_apod(), display_photo_on_canvas())
    get_apod()
    display_photo_on_canvas()


root = Tk()
root.geometry('600x730')
root.resizable(width=False, height=False)
root.title("Astronomy picture of the day")
show_instructions()
bg_image = Image.open('../images/label_bg_image.jpg')
bg_image = bg_image.resize((700, 800), Image.Resampling.LANCZOS)
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

add_to_starred = Button(
    text='❤Star⭐', bg=BUTTON_COLOR,
    command=add_starred_to_file
)
add_to_starred.config(state=DISABLED)
add_to_starred.place(x=80, y=667)
root.bind('<Control-f>', add_starred_to_file)

show_starred_button = Button(text='See starred', bg=BUTTON_COLOR, command=show_starred)
show_starred_button.place(x=3, y=667)
root.bind('<Control-d>', show_starred)

instructions_button = Button(text='Instructions', bg=BUTTON_COLOR, command=show_instructions)
instructions_button.place(x=30, y=700)
root.bind('<Control-i>', show_instructions)

save_button = Button(text='Save', bg=BUTTON_COLOR, command=save_apod)
save_button.place(x=150, y=700)


canvas = Canvas(width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=CANVAS_COLOR, highlightthickness=0)

original_bg_image = Image.open('../images/canvas_bg_image.jpg')
resized_bg_image = original_bg_image.resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.Resampling.LANCZOS)

tk_image = ImageTk.PhotoImage(resized_bg_image)
canvas_bg = canvas.create_image(300, 300, image=tk_image)
intro_text = canvas.create_text(
                10, 100, text='Fetch stunning Astronomy\n'
                              'Photos of the Day\n'
                              'from NASA’s API\n'
                              'and save them — you\n'
                              'might just discover\n'
                              'your next wallpaper! 😉',
                fill='white', font=("Helvetica", 20, "italic"),
                anchor="w"
            )
title_text = canvas.create_text(300, 20, text='', font=('Arial', 14, 'bold'), fill='white')
explanation_text = canvas.create_text(300, 440, text='', font=('poppins', 12, 'italic'), fill='white',
                                      width=580)

canvas.grid(column=0, row=0, columnspan=2)

root.mainloop()
