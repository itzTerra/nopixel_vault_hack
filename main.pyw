# Tkinter app trying to replicate bank hack minigame from NoPixel GTA V RP server.

from tkinter import *
from tkinter.ttk import OptionMenu
from tkinter.font import Font
import random
from PIL import ImageTk, Image
# from time import perf_counter

from puzzle_gen import *
import lerp


def geocenter(size: str):
    intsize = [int(i) for i in size.split("x")]
    x = (1920 - intsize[0]) // 2
    y = (1080 - intsize[1]) // 2
    root.geometry(f"{size}+{x}+{y}")


root = Tk()
root.title("Hack Minigame")
root.iconphoto(True, PhotoImage(file="img/spy-icon_32.png"))
geocenter("1200x700")
root.resizable(False, False)

C_PRIMARY = "#20242E"
C_SECONDARY = "#2E4561"
root.config(bg=C_PRIMARY)

font_intro = Font(family="Archivo Black", size=18)
font_small = Font(family="Arial", size=13)
font_smaller = Font(family="Arial", size=11)
font_text = Font(family="Archivo Black", size=21)
font_question = Font(family="Archivo Black", size=13)
font_num = Font(family="Arial", size=60)
big_num = Font(family="Arial", size=160)
root.option_add("*Font", "Arial 13")

# ===================== CONSTANTS ========================
INTRO_QUOTES = [
    "DEVICE BOOTING UP...",
    "DIALING...",
    "ESTABLISHING CONNECTION...",
    "DOING SOME HACKERMANS STUFF...",
    "ACCESS CODE FLAGGED; REQUIRES HUMAN CAPTCHA INPUT...",
]

SHAPE_COORDS = {
    "square": (30, 230, 230, 230, 230, 30, 30, 30),
    "rectangle": (30, 190, 230, 190, 230, 70, 30, 70),
    "triangle": (30, 230, 230, 230, 130, 30),
}

# Difficulty changes time in seconds to beat a round
DIFFICULTIES = {"Easy": 15, "Normal": 9, "Hard": 5}

# ORIGINAL TIMINGS ARE SLOWED DOWN, THIS IS A COUNTERMEASURE
for diff in DIFFICULTIES:
    DIFFICULTIES[diff] *= 0.65

ROUNDS_TO_WIN = 5

# Delay in ms between intro quotes
INTRO_QUOTE_DELAY = 500

# ====================== HELPERS AND INIT =======================

def draw_outline_text(canvas: Canvas, x: int, y: int, color: str, font, text: str):
    # Outline logic
    outline = "black"
    if color == "black":
        outline = "white"

    canvas.create_text(
        x + 1,
        y + 1,
        fill=outline,
        font=font_text,
        text=text,
    )
    canvas.create_text(
        x,
        y,
        fill=color,
        font=font_text,
        text=text,
    )


def draw_square(canvas: Canvas, square: Square):
    if square.shape == "circle":
        canvas.create_oval(30, 230, 230, 30, fill=square.shape_color)
    else:
        canvas.create_polygon(SHAPE_COORDS.get(square.shape), fill=square.shape_color)

    draw_outline_text(
        canvas,
        130,
        92,
        square.text_background_color,
        font_text,
        square.color_text.upper(),
    )
    draw_outline_text(
        canvas,
        130,
        172,
        square.text_background_color,
        font_text,
        square.shape_text.upper(),
    )
    canvas.create_text(
        130,
        130,
        fill=square.number_color,
        font=font_num,
        text=str(random.randint(1, 9)),
    )


def clear_screen():
    for widget in root.winfo_children():
        try:
            widget.place_forget()
        except:
            try:
                widget.grid_forget()
            except:
                widget.pack_forget()


puzzleGenerator = PuzzleGenerator()
current_round = 1
ANSWER_PLACEHOLDER = "blue square"
answer_var = StringVar(value=ANSWER_PLACEHOLDER)
time_to_answer_sec = 7

# ========================= COMPONENTS =======================
canvas_frame = Frame(root, bg=C_PRIMARY)
canvases = [
    Canvas(
        canvas_frame,
        width=260,
        height=260,
        bg=C_SECONDARY,
        bd=0,
        highlightthickness=0,
    )
    for _ in range(4)
]

win_label = Label(
    root,
    text="THE SYSTEM HAS BEEN BYPASSED.",
    font=font_intro,
    fg="white",
    bg=C_PRIMARY,
)

win_img_canvas = Canvas(
    root,
    width=70,
    height=73,
    bg=C_PRIMARY,
    bd=0,
    highlightthickness=0,
)
win_img = Image.open("img/spy-icon.png")
win_img = win_img.resize((70, 73), Image.Resampling.LANCZOS)
root.win_img = win_img = ImageTk.PhotoImage(win_img)
win_img_canvas.create_image(0, 0, image=win_img, anchor=NW)

fail_label = Label(
    root,
    justify=LEFT,
    bg=C_PRIMARY,
    fg="white",
    font=font_smaller,
)

fail_img_canvas = Canvas(
    root,
    width=62,
    height=62,
    bg=C_PRIMARY,
    bd=0,
    highlightthickness=0,
)
fail_img = Image.open("img/failed.png")
fail_img = fail_img.resize((62, 62), Image.Resampling.LANCZOS)
root.fail_img = fail_img = ImageTk.PhotoImage(fail_img)
fail_img_canvas.create_image(0, 0, image=fail_img, anchor=NW)


question_label = Label(
    root,
    font=font_question,
    fg="white",
    bg=C_PRIMARY,
)

answer_frame = Frame(root, bg=C_PRIMARY)
Label(
    answer_frame,
    text="Answer",
    justify=LEFT,
    bg=C_PRIMARY,
    fg="white",
    font=font_smaller,
).grid(row=0, columnspan=2, sticky=W, pady=4)

# Small icon next to input
entry_img_canvas = Canvas(
    answer_frame, width=18, height=19, bg=C_PRIMARY, bd=0, highlightthickness=0
)
entry_img_canvas.grid(row=1, column=0, padx=3)
entry_img = Image.open("img/spy-icon.png")
entry_img = entry_img.resize((18, 19), Image.Resampling.LANCZOS)
answer_frame.img = entry_img = ImageTk.PhotoImage(entry_img)
entry_img_canvas.create_image(0, 0, image=entry_img, anchor=NW)

# Input box with binds
answerbox = Entry(
    answer_frame,
    bg=C_PRIMARY,
    fg="grey",
    bd=0,
    textvariable=answer_var,
    insertbackground="white",
    insertwidth=1,
    font=font_small,
)
answerbox.grid(row=1, column=1, padx=5)
# Cosmetic line
answerbox_line = Frame(root, width=212, height=2)

# ========================= LOGIC =======================

def once(event):
    answer_var.set("")
    answerbox.config(fg="white")
    answerbox.unbind("<Key>")
answerbox.bind("<Key>", once)


def clear_answer(placeholder=ANSWER_PLACEHOLDER):
    answer_var.set(placeholder)
    answerbox.config(fg="grey")
    answerbox.bind("<Key>", once)


def blank_check(event):
    if len(answer_var.get()) == 1:
        clear_answer(" "+ANSWER_PLACEHOLDER)
answerbox.bind("<BackSpace>", blank_check)


def evaluate(event):
    global current_round

    if isinstance(event, int) and event < current_round:
        return

    clear_screen()

    answer = answer_var.get()

    if answer == puzzleGenerator.good_answer:
        current_round += 1
        if current_round == ROUNDS_TO_WIN:
            # WIN
            win_img_canvas.place(relx=0.5, rely=0.4, anchor=CENTER)
            win_label.place(relx=0.5, rely=0.5, anchor=CENTER)
            menu_button.place(relx=0.5, rely=0.6, anchor=CENTER)
            return
        start_round()
    else:
        # FAIL
        fail_img_canvas.place(relx=0.5, rely=0.35, anchor=CENTER)
        fail_label.config(text="The answer was: " + puzzleGenerator.good_answer)
        fail_label.place(relx=0.5, rely=0.6, anchor=CENTER)
        menu_button.place(relx=0.5, rely=0.5, anchor=CENTER)
answerbox.bind("<Return>", evaluate)


def start_puzzle():
    # Draw squares
    for i, canvas in enumerate(canvases):
        square = puzzleGenerator.squares[i]
        canvas.config(bg=square.background_color)
        draw_square(canvas, square)

    # Draw question
    question_label.config(text=puzzleGenerator.question)
    question_label.place(relx=0.5, rely=0.75, anchor=CENTER)

    # Draw input field
    answer_frame.place(relx=0.5, rely=0.9, anchor=CENTER)
    clear_answer()
    answerbox.focus_set()
    answerbox.icursor(0)
    answerbox_line.place(relx=0.5, rely=0.944, anchor=CENTER)

    # Draw timer
    TIMER_WIDTH = 1128
    timer_back = Frame(root, width=TIMER_WIDTH, height=4, bg="#754E2E")
    timer_back.place(relx=0.5, rely=0.65, anchor=CENTER)
    timer_frame = Frame(root, width=TIMER_WIDTH, height=4, bg="#E7A26D")
    timer_frame.place(relx=0.5, rely=0.65, anchor=CENTER)

    TIMER_DECREMENT_MS = 10
    timer_time = DIFFICULTIES[difficulty_var.get()] * 1000
    timer_decrement_px = lerp.remap(0, timer_time, 0, TIMER_WIDTH, TIMER_DECREMENT_MS)

    cur_round = current_round

    # Timer animation
    def timer(time_ms, width):
        if time_ms <= 0:
            # print(perf_counter() - tic)
            evaluate(cur_round)
            return

        timer_frame.config(width=width)
        root.after(
            TIMER_DECREMENT_MS,
            timer,
            time_ms - TIMER_DECREMENT_MS,
            width - timer_decrement_px,
        )
    # tic = perf_counter()
    timer(timer_time, TIMER_WIDTH)


# Key index animation, puzzle start
def shrink_indexes(size=160):
    if size > 0:
        big_num.config(size=size)
        root.after(10, shrink_indexes, size - 2)
    else:
        for canvas in canvases:
            canvas.delete(ALL)
        big_num.config(size=160)

        root.after(100, start_puzzle)


def start_round():
    # Frame for grid placement of game squares (canvases), precomputing canvases in the frame - not yet placing
    canvas_frame.place(relx=0.5, rely=0.3, anchor=CENTER)

    puzzleGenerator.generate()

    # Canvas placement with starting key indexes
    for i, canvas in enumerate(canvases):
        canvas.delete(ALL)
        canvas.config(bg=C_SECONDARY)
        canvas.grid(row=0, column=i, padx=15)
        canvas.create_text(
            130, 130, fill="white", font=big_num, text=str(puzzleGenerator.indexes[i])
        )

    root.after(1500, shrink_indexes)


# Intro to the game (from quotes list)
intro_label = Label(root, font=font_intro, fg="white", bg=C_PRIMARY)

def play_intro(i=0):
    if i == 0:
        intro_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    if i < len(INTRO_QUOTES):
        intro_label.config(text=INTRO_QUOTES[i])
        root.after(INTRO_QUOTE_DELAY, lambda: play_intro(i + 1))
    else:
        intro_label.place_forget()

        root.after(300, start_round)


def start_game():
    global current_round
    current_round = 1
    clear_screen()
    root.after(300, play_intro)


diff_frame = Frame(root, bg=C_SECONDARY)
diff_label = Label(
    diff_frame, text="Choose difficulty:", font=font_small, fg="white", bg=C_SECONDARY
)
diff_label.pack(side=LEFT)

difficulty_var = StringVar(value="Normal")
diff_select = OptionMenu(
    diff_frame, difficulty_var, difficulty_var.get(), *DIFFICULTIES.keys()
)
diff_select.pack(side=LEFT)

start_button = Button(
    root,
    text="START",
    command=start_game,
    cursor="hand2",
    font=font_intro,
    fg="white",
    bg=C_SECONDARY,
    relief="flat",
    width=11
)

exit_button = Button(
    root,
    text="EXIT",
    command=root.destroy,
    cursor="hand2",
    font=font_intro,
    fg="white",
    bg="#ff2222",
    relief="flat",
    width=11
)

def go_main_menu():
    clear_screen()
    diff_frame.place(relx=0.5, rely=0.4, anchor=CENTER)
    start_button.place(relx=0.5, rely=0.5, anchor=CENTER)
    exit_button.place(relx=0.5, rely=0.62, anchor=CENTER)


menu_button = Button(
    root,
    text="MAIN MENU",
    command=go_main_menu,
    cursor="hand2",
    font=font_intro,
    fg="white",
    bg=C_SECONDARY,
    relief="flat",
)

go_main_menu()

# Program start
mainloop()
