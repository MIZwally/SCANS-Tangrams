from psychopy import visual, core, event, gui
import os, random, csv, time
##Tangrams code for BBI Project 6/30/2025

## Loading screen for participant ID and how to change file order(update the file thing)
info = {'Participant ID': '', 'Run Order (comma-separated)': 'W,Z,L'}
dlg = gui.DlgFromDict(info)
if not dlg.OK:
    core.quit()

participant_id = info['Participant ID']
custom_folder_order = [folder.strip() for folder in info['Run Order (comma-separated)'].split(',')]

## For Saving file path and data(not sure if this is working yet)
save_path = f"data/{participant_id}"
os.makedirs(save_path, exist_ok=True)

csv_file = os.path.join(save_path, f"{participant_id}_responses.csv")
csv_headers = ['participant', 'block', 'folder', 'role',
               'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6',
               'selected_indices', 'response_time', 'status']

with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(csv_headers)

## Window set up(change window size based on computer used)
win = visual.Window(size=(1500, 850), fullscr=False, color='black', units='pix')
mouse = event.Mouse(visible=True, win=win)

## Instruction section change for if needed
fixation = visual.TextStim(win, text='+', height=50, color='white')
thanks = visual.TextStim(win, text="Thank you for participating!", color='white')
rest = visual.TextStim(win, text='[Rest / Break Video Playing Here]', color='white')
instruction_text = visual.TextStim(win, text='', height=30, wrapWidth=1400, color='white', pos=(0, 300))

## Image pathway(make sure youy edit directory before running task and that you have the right folders downloaded)
base_dir = '/Users/dscn/Desktop/Tangrams'
control_folder = 'Control'

all_images = {}
for folder in custom_folder_order:
    full_path = os.path.join(base_dir, folder)
    if os.path.exists(full_path):
        all_images[folder] = [
            os.path.join(full_path, f)
            for f in os.listdir(full_path)
            if f.endswith(('.jpg', '.png'))
        ]
    else:
        all_images[folder] = []

control_images_pool = [
    os.path.join(base_dir, control_folder, f)
    for f in os.listdir(os.path.join(base_dir, control_folder))
    if f.endswith(('.jpg', '.png'))
]

used_images = []

def log_response(participant, block, folder, role, images, selections, rt, status="completed"):
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        row = [participant, block, folder, role] + images + [','.join(map(str, selections)), rt, status]
        writer.writerow(row)

##Utility functions
def check_escape():
    if 'escape' in event.getKeys():
        log_response(participant_id, 'N/A', 'N/A', 'N/A', ['']*6, [], 0.0, status="early_exit")
        win.close()
        core.quit()

def wait_for_space():
    while True:
        keys = event.getKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            check_escape()
        if 'space' in keys:
            break
        core.wait(0.1)

def show_fixation(duration=3):
    fixation.draw()
    win.flip()
    core.wait(duration)
    check_escape()

def show_rest_video():
    rest.draw()
    win.flip()
    core.wait(10)
    check_escape()

def select_images(folder, num=6):
    available = list(set(all_images[folder]) - set(used_images))
    if len(available) < num:
        raise ValueError(f"Not enough unique images remaining in folder {folder}")
    selected = random.sample(available, num)
    used_images.extend(selected)
    return selected

def select_control_images(num=6):
    return random.sample(control_images_pool, num)

def show_instructions(role):
    check_escape()
    if role == 'guessor':
        instruction = (
            "You are the GUESSOR.\n\n"
            "The director will describe one of the images.\n"
            "Click a box (A–F) to type your guess.\n"
            "You can change your responses anytime during the round.\n\n"
            "You have 2 minutes.\n\nPress SPACE to begin."
        )
    else:
        instruction = (
            "You are the DIRECTOR.\n\n"
            "You will see one image at a time.\n"
            "Describe each image to the guessor.\n\n"
            "Each image will appear for 20 seconds.\n\nPress SPACE to begin."
        )
    instruction_text.text = instruction
    instruction_text.draw()
    win.flip()
    wait_for_space()

def guessor_block(images, block_num, folder):
    positions = [(-400, 250), (0, 250), (400, 250), (-400, -50), (0, -50), (400, -50)]
    image_stims = [visual.ImageStim(win, image=img, pos=pos, size=(250, 250))
                   for img, pos in zip(images, positions)]

    alpha_labels = ["A", "B", "C", "D", "E", "F"]
    image_labels = [visual.TextStim(win, text=lbl, pos=(pos[0], pos[1]-160), color='white', height=30)
                    for lbl, pos in zip(alpha_labels, positions)]

    box_positions = [(700, 200), (700, 150), (700, 100), (700, 50), (700, 0), (700, -50)]
    input_boxes = [visual.TextBox2(win, text='', pos=pos, letterHeight=24,
                               size=(100, 30), color='white', borderColor='white')
               for pos in box_positions]

    prompt = visual.TextStim(win, text="Click a box to type. Press ENTER to submit. Press ESC to quit.",
                             pos=(0, -400), color='white', height=26)

    start_time = time.time()
    max_duration = 120

    active_box_index = None

    while time.time() - start_time < max_duration:
        check_escape()

        for stim in image_stims:
            stim.draw()
        for label in image_labels:
            label.draw()
        for idx, box in enumerate(input_boxes):
            label = visual.TextStim(win, text=f"{idx+1}", pos=(box.pos[0] - 70, box.pos[1]), color='white', height=20)
            label.draw()
            box.draw()

        prompt.draw()
        win.flip()

        if mouse.getPressed()[0]:
            for idx, box in enumerate(input_boxes):
                if box.contains(mouse):
                    active_box_index = idx
                    break

        keys = event.getKeys()
        for key in keys:
            check_escape()
            if key == 'return':
                responses = [box.text for box in input_boxes]
                rt = round(time.time() - start_time, 3)
                log_response(participant_id, block_num, folder, 'guessor', images, responses, rt)
                return
            elif active_box_index is not None:
                if key == 'backspace':
                    input_boxes[active_box_index].text = input_boxes[active_box_index].text[:-1]
                elif len(key) == 1:
                    input_boxes[active_box_index].text += key

def director_block(images, block_num, folder):
    for img_path in images:
        stim = visual.ImageStim(win, image=img_path, size=(600, 600))
        stim.draw()
        win.flip()
        start = time.time()
        while time.time() - start < 20:
            check_escape()
            core.wait(0.1)

    rt = 120.0
    log_response(participant_id, block_num, folder, 'director', images, [], rt)

def control_block(images, role, block_num):
    check_escape()
    if role == 'guessor':
        guessor_block(images, f"{block_num}_control", 'control')
    else:
        director_block(images, f"{block_num}_control", 'control')

## Loop for task (might need editing for rest video)
role = 'guessor'
block_count = 8

for block_num in range(1, block_count + 1):
    check_escape()
    folder_index = (block_num - 1) // 2
    folder = custom_folder_order[folder_index % len(custom_folder_order)]

    show_fixation()
    if block_num in [4, 7]:
        show_rest_video()

    show_instructions(role)
    images = select_images(folder, 6)

    if role == 'guessor':
        guessor_block(images, block_num, folder)
    else:
        director_block(images, block_num, folder)

    control_imgs = select_control_images(6)
    control_block(control_imgs, role, block_num)

    role = 'director' if role == 'guessor' else 'guessor'

## For the end of the task
thanks.draw()
win.flip()
core.wait(5)
win.close()
core.quit()
