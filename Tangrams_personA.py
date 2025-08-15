from psychopy import visual, core, event, gui
import os, random, csv, time, math
##Tangrams code for SCANS Project 6/30/2025

## Loading screen for participant ID and how to change file order(update the file thing)
info = {'Dyad ID:': '', 'Subject ID': '', 'Participant #': '1', 'Run Order': 'KWN'}
dlg = gui.DlgFromDict(info, title="Tangrams", order=list(info.keys()))
if not dlg.OK:
    core.quit()

code_interpreter = {'K': 'easyA,hardA', 'L': 'easyA,hardB', 'M': 'easyB,hardA', 'N': 'easyB,hardB', 
                    'W': 'controlA,controlC', 'X': 'controlA,controlD', 'Y': 'controlB,controlC', 'Z': 'controlB,controlD'}

trial_folders = ['easyA', 'hardA', 'easyB', 'hardB']
control_folders = ['controlA', 'controlB', 'controlC', 'controlD']

participant_id = info['Subject ID']
custom_folder_order = []
if len(info['Run Order']) != 3 :
    raise ValueError('Invalid run order; run order must be 3 letters')
for code in info['Run Order'] :
    code = code.capitalize()
    if code not in code_interpreter.keys() :
        raise ValueError(f'{code} is not a valid run code')
    [custom_folder_order.append(k) for k in code_interpreter[code].split(',')]

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
win = visual.Window(size=(1500, 850), fullscr=False, color=[0,0,0], units='pix')
mouse = event.Mouse(visible=True, win=win)

## Instruction section change for if needed
fixation = visual.TextStim(win, text='+', height=50, color='white')
thanks = visual.TextStim(win, text="Thank you for participating!", color='white')
rest = visual.TextStim(win, text='[Rest / Break Video Playing Here]', color='white')
instruction_text = visual.TextStim(win, text='', height=30, wrapWidth=1400, color='white', pos=(0, 300), anchorVert='top')

## Image pathway(make sure youy edit directory before running task and that you have the right folders downloaded)
base_dir = '\\Users\\mizwa\\Desktop\\SCANS Tangrams\\Tangrams_images'

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

def check_escape2(key):
    if key == 'escape':
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
    print(available)
    if len(available) < num:
        raise ValueError(f"Not enough unique images remaining in folder {folder}")
    selected = random.sample(available, num)
    used_images.extend(selected)
    return selected

def show_instructions(role, control):
    if control :
        control_instructions = 'SOLO'
    else :
        control_instructions = 'TOGETHER'
    check_escape()
    if role == 'guessor':
        instruction = (
            f"{control_instructions} \n\n"
            "You are the GUESSOR.\n\n"
            "The director will describe one of the images.\n"
            "Click a box (A–F) to type your guess.\n"
            "You can change your responses anytime during the round.\n\n"
            "You have 2 minutes.\n\nPress SPACE to begin."
        )
    else:
        instruction = (
            f"{control_instructions} \n\n"
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
            check_escape2(key)
            if key == 'return' and ((time.time() - start_time) < 105) :
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
if info['Participant #'] == '1' :
    role = 'director'
elif info['Participant #'] == '2' :
    role = 'guessor'
block_count = 12
block_num = 0

while block_num < block_count :
    block_num += 1
    
    folder_index = int(math.ceil(block_num / 2)) - 1
    check_escape()
    folder = custom_folder_order[folder_index]

    show_fixation()

    ctrl = False
    print(folder)
    if folder in control_folders :
        ctrl = True
    
    show_instructions(role, ctrl)
    images = select_images(folder, 6)
    # add if control block change instructions??
    if role == 'guessor':
        guessor_block(images, block_num, ctrl)
    else:
        director_block(images, block_num, ctrl)

    role = 'director' if role == 'guessor' else 'guessor'

## For the end of the task
thanks.draw()
win.flip()
core.wait(5)
win.close()
core.quit()
