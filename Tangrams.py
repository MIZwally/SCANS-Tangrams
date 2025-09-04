from psychopy import visual, core, event, gui
import os, random, csv, time, math
from pylsl import StreamInfo, StreamOutlet
from sys import platform

##Tangrams code for SCANS Project 6/30/2025


info = StreamInfo(name='Trigger', type='Markers', channel_count=1, channel_format='int32', source_id='Tangrams')  # pyright: ignore[reportArgumentType]
outlet = StreamOutlet(info)

## Loading screen for participant ID and how to change file order(update the file thing)
info = {'Dyad ID:': '', 'Subject ID': '', 'Participant #': '2', 'Run Order': 'KWN'}
dlg = gui.DlgFromDict(info, title="Tangrams", order=list(info.keys()))
if not dlg.OK:
    core.quit()

code_interpreter = {'K': 'easyA,hardA', 'L': 'easyA,hardB', 'M': 'easyB,hardA', 'N': 'easyB,hardB', 
                    'W': 'controlA,controlC', 'X': 'controlA,controlD', 'Y': 'controlB,controlC', 'Z': 'controlB,controlD'}

trial_folders = {'easyA': 1, 'hardA': 2, 'easyB': 3, 'hardB': 4}
control_folders = {'controlA': 1, 'controlB': 2, 'controlC': 3, 'controlD': 4}

custom_folder_order = []
if len(info['Run Order']) != 3 :
    raise ValueError('Invalid run order; run order must be 3 letters')
for code in info['Run Order'] :
    code = code.capitalize()
    if code not in code_interpreter.keys() :
        raise ValueError(f'{code} is not a valid run code')
    [custom_folder_order.append(k) for k in code_interpreter[code].split(',')]

participant_id = info['Subject ID']
if info['Participant #'] != '1' and info['Participant #'] != '2' :
    raise ValueError('Participant # must be either 1 or 2')

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
outlet.push_sample(x=[000])
print(000)
## Image pathway(make sure youy edit directory before running task and that you have the right folders downloaded)
#checking if windows or mac
if platform == "darwin":
    print('Mac OS')
    base_dir = '/Users/mizwally/Desktop/SCANS-Tangrams/Tangrams_images'
elif platform == "win32":
    print('Windows')
    base_dir = '\\Users\\mizwa\\Desktop\\SCANS-Tangrams\\Tangrams_images'


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
    positions = [(-400, 250), (0, 250), (400, 250), (-400, -120), (0, -120), (400, -120)]
    image_stims = [visual.ImageStim(win, image=img, pos=pos, size=(250, 250))
                   for img, pos in zip(images, positions)]

    box_positions = [(-400, 70), (0, 70), (400, 70), (-400, -300), (0, -300), (400, -300)]
    input_boxes = [visual.TextBox2(win, text='', pos=pos, letterHeight=24, editable=True,
                            size=(110, 35), placeholder='', color='black', fillColor='white',
                            borderColor='black') for pos in box_positions]

    start_time = time.time()
    max_duration = 120

    active_box_index = None

    while time.time() - start_time < max_duration:
        check_escape()

        for stim in image_stims:
            stim.draw()
        for box in input_boxes:
            box.draw()

        win.flip()
        
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

## Loop for task (might need editing for rest video)
    
block_count = 6
block_num = 0
task_blocks = 0

while block_num < block_count :
    folder_index = block_num
    check_escape()
    folder = custom_folder_order[folder_index]
    #task vs control code (1st digit)
    ctrl = False
    if folder in control_folders :
        condition = 1
        ctrl = True
    else :
        condition = 2
        task_blocks += 1
    
    images = select_images(folder, 6)
    
    if ctrl == True :
        if info['Participant #'] == '1' :
            role = 'director' if block_num % 2 == 0 else 'guessor'
        else :
            role = 'guessor' if block_num % 2 == 0 else 'director'
    else :
        if task_blocks in [1, 4] :
           role = 'director' if info['Participant #'] == '1' else 'guessor'
        elif task_blocks in [2, 3] :
           role = 'guessor' if info['Participant #'] == '1' else 'director'
    
    for i in range(2) :
        #Creating Trigger Code
        #which folder is being used (2nd digit)
        folder_code = control_folders[folder] if ctrl else trial_folders[folder]
        #role code (3rd digit)
        director = 1 if role == 'director' else 2
        #first vs repeat block (last digit)
        repeat = 1 if i == 0 else 2
        #assemble trigger
        trigger = condition*1000 + folder_code*100 + director*10 + repeat
        
        outlet.push_sample(x=[777])
        show_fixation()
        
        outlet.push_sample(x=[444])
        show_instructions(role, ctrl)
        
        outlet.push_sample(x=[trigger])
        print(trigger)
        if role == 'guessor':
            guessor_block(images, block_num, ctrl)
        else:
            director_block(images, block_num, ctrl)
            
        role = 'director' if role == 'guessor' else 'guessor'
    
    block_num += 1

## For the end of the task
thanks.draw()
outlet.push_sample(x=[999])
win.flip()
core.wait(5)
win.close()
core.quit()


'''
from psychopy import visual, event

# Set up the PsychoPy window
win = visual.Window([800, 600], color="white", units="pix")

instruction = visual.TextStim(win, text="Select a condition from the dropdown:", pos=(0, 250))

# Dropdown options and the button
dropdown_rect = visual.Rect(win, width=300, height=50, pos=(0, 100), fillColor="lightgray", lineColor="white") # type: ignore
dropdown_text = visual.TextStim(win, text="Condition A", pos=(0, 100))

# List of options for the dropdown
options = ['Condition A', 'Condition B', 'Condition C']
option_rects = []
option_texts = []

# Create visual elements for each option below the button
for i, option in enumerate(options):
    option_rects.append(visual.Rect(win, width=300, height=50, pos=(0, 100 - (i + 1) * 55), fillColor="lightgray", lineColor="white")) # type: ignore
    option_texts.append(visual.TextStim(win, text=option, pos=(0, 100 - (i + 1) * 55)))

# Track whether the dropdown is open or closed
dropdown_open = False
current_option_index = 0

# Set up mouse input
mouse = event.Mouse(win=win)

# Experiment loop
while True:
    # Draw the instructions
    instruction.draw()
    
    # Draw the dropdown button
    dropdown_rect.draw()
    dropdown_text.draw()

    # If the dropdown is open, draw the options
    if dropdown_open:
        for rect, text in zip(option_rects, option_texts):
            rect.draw()
            text.draw()

    # Check for mouse clicks on the dropdown button
    if mouse.isPressedIn(dropdown_rect) and not dropdown_open:
        dropdown_open = True  # Open the dropdown menu

    # Check for mouse clicks on any option
    for i, rect in enumerate(option_rects):
        if mouse.isPressedIn(rect):
            dropdown_text.setText(options[i])  # Update the text to the selected option
            dropdown_open = False  # Close the dropdown menu after selection

    # Check for quitting the experiment (press 'q')
    if 'q' in event.getKeys():
        break

    # Update the window
    win.flip()

# Close the window after the loop ends
win.close()

'''