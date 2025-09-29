from psychopy import visual, core, event, gui
import os, random, csv, time, math
from pylsl import StreamInfo, StreamOutlet
from sys import platform

##Tangrams code for SCANS Project 6/30/2025


info = StreamInfo(name='Trigger', type='Markers', channel_count=1, channel_format='int32', source_id='Tangrams')  # pyright: ignore[reportArgumentType]
outlet = StreamOutlet(info)

## Loading screen for participant ID and how to change file order(update the file thing)
info = {'Dyad ID': '', 'Subject ID': '', 'Participant #': '2', 'Run Order': 'DZN'}
dlg = gui.DlgFromDict(info, title="Tangrams", order=list(info.keys()))
if not dlg.OK:
    core.quit()

code_interpreter = {"C": "easyA,hardA", "D": "easyA,hardB", "E": "easyA,hardC", "F": "easyA,hardD",
                    "G": "easyB,hardA", "H": "easyB,hardB", "I": "easyB,hardC", "J": "easyB,hardD",
                    "K": "easyC,hardA", "L": "easyC,hardB", "M": "easyC,hardC", "N": "easyC,hardD",
                    "O": "easyD,hardA", "P": "easyD,hardB", "Q": "easyD,hardC", "R": "easyD,hardD",
                    'Z': 'control,control'}

folder_code_dict = {'easyA': 1, 'hardA': 2, 'easyB': 3, 'hardB': 4, 'easyC': 5, 'hardC': 6, 'easyD': 7, 'hardD': 8}
control_index = []
custom_folder_order = []
if len(info['Run Order']) != 3 :
    raise ValueError('Invalid run order; run order must be 3 letters')
for code in info['Run Order'] :
    code = code.capitalize()
    if code not in code_interpreter.keys() :
        raise ValueError(f'{code} is not a valid run code')
    if code == 'Z' :
        control_index.append(True)
    else :
        control_index.append(False)
    [custom_folder_order.append(k) for k in code_interpreter[code].split(',')]

control_options = [f for f in folder_code_dict.keys() if f not in custom_folder_order]

participant_id = info['Subject ID']
if info['Participant #'] != '1' and info['Participant #'] != '2' :
    raise ValueError('Participant # must be either 1 or 2')

## For Saving file path and data(not sure if this is working yet)
save_path = f"data/{info['Dyad ID']}"
os.makedirs(save_path, exist_ok=True)

csv_file = os.path.join(save_path, f"{info['Dyad ID']}_{participant_id}_responses.csv")
csv_headers = ['Block', 'Control?', 'Folder', 'Role',
               'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6',
               'input_1', 'input_2', 'input_3', 'input_4', 'input_5', 'input_6',
               'response_time', 'status']

with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(csv_headers)

## Window set up(change window size based on computer used)
win = visual.Window(size=(1500, 850), fullscr=False, color=[0,0,0], units='pix')
mouse = event.Mouse(visible=True, win=win)

## Instruction section change for if needed
fixation = visual.TextStim(win, text='+', height=50, color='white')
thanks = visual.TextStim(win, text="Thank you for participating!", color='white')
instruction_text = visual.TextStim(win, text='', height=30, wrapWidth=1400, color='white', pos=(0, 300), anchorVert='top')
outlet.push_sample(x=[0])
print(0)
## Image pathway (make sure youy edit directory before running task and that you have the right folders downloaded)
#checking if windows or mac
if platform == "darwin":
    print('Mac OS')
    base_dir = '/Users/mizwally/Desktop/SCANS-Tangrams/Tangrams_images'
    #SCaNS 1
    #base_dir = '/Users/dscnuser/Desktop/SCANS-Tangrams/Tangrams_images'
    #SCaNS 2
    #base_dir = '/Users/dscn/Desktop/SCANS-Tangrams/Tangrams_images'
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

def log_response(block, condition, folder, role, images, selections, rt, status="completed"):
    img_names = [os.path.basename(img) for img in images]
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        #row = [block, condition, folder, role] + img_names + [','.join(map(str, selections)), rt, status]
        row = [block, condition, folder, role] + img_names + selections + [rt, status]
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

def select_images(folder, num=6):
    full_path = os.path.join(base_dir, folder)
    if os.path.exists(full_path):
        images = [
            os.path.join(full_path, f)
            for f in os.listdir(full_path)
            if f.endswith(('.jpg', '.png'))
        ]
    else:
        images = []
    #available = list(set(all_images[folder]) - set(used_images))
    #if len(available) < num:
    #    raise ValueError(f"Not enough unique images remaining in folder {folder}")
    selected = random.sample(images, num)
    used_images.extend(selected)
    return selected

def show_instructions(role, control):
    if control :
        control_instructions = 'You and your partner will NOT see the same images.\n\n'
    else :
        control_instructions = ' '
    check_escape()
    if role == 'guessor':
        instruction = (
            f"You are the GUESSOR.\n\n"
            "You will see 6 images. The director will describe an image to you\n"
            "and you have to guess which of the 6 they are describing.\n\n"
            "Type the image number (1-6) into the box below the image.\n"
            "You can change your responses anytime during the round.\n\n"
            f"{control_instructions}"
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

def guessor_block(block_num, ctrl, folder, images):
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
    last_text = [''] * 6
    current_text = [''] * 6
    responses = [[] for _ in range(6)]
    
    while time.time() - start_time < max_duration:
        check_escape()

        for stim in image_stims:
            stim.draw()
        for box in input_boxes:
            #only allow numbers 1-6        
            allowed = ['1', '2', '3', '4', '5', '6', 'backspace'] 
            box.text = "".join(ch for ch in box.text if ch.lower() in allowed)
            if len(box.text) > 1:
                box.text = box.text[0]
            box.draw()

        win.flip()
        
        #for saving values every time they change 
        for i, box in enumerate(input_boxes) :
            current_text[i] = box.text
            if current_text[i] != "" and current_text[i] != last_text[i]:
                last_text[i] = current_text[i]  # update tracker
                responses[i].append((current_text[i], round(time.time() - start_time, 3)))
        
        keys = event.getKeys()
        for key in keys:
            check_escape2(key)
            if key == 'return' and ((time.time() - start_time) < 105) :
                #responses = [box.text for box in input_boxes]
                rt = round(time.time() - start_time, 3)
                log_response(block_num, ctrl, folder, 'guessor', images, responses, rt)
                return
            elif active_box_index is not None:
                if key == 'backspace':
                    input_boxes[active_box_index].text = input_boxes[active_box_index].text[:-1]
                elif len(key) == 1:
                    input_boxes[active_box_index].text += key
                    
    log_response(block_num, ctrl, folder, 'guessor', images, responses, 120.0)
        
def director_block(block_num, ctrl, folder, images):
    for i, img_path in enumerate(images, start=1):
        stim = visual.ImageStim(win, image=img_path, size=(550, 550))
        counter = visual.TextStim(win, text=str(i), pos=(600, -300), color='white', height=30)
        stim.draw()
        counter.draw()
        win.flip()
        start = time.time()
        while time.time() - start < 20:
            check_escape()
            core.wait(0.1)

    responses = [] * 6
    log_response(block_num, ctrl, folder, 'director', images, responses, 120.0)
    

def get_control_folder(block_num, increment, f) :
    i = 0
    folder = f
    if block_num % 2 == 0 :
        while folder == 'control' :
            if 'easy' in control_options[i] :
                folder = control_options[i]
            i += increment
    else :
        while folder == 'control' :
            if 'hard' in control_options[i] :
                folder = control_options[i]
            i += increment
    return folder
        
block_count = 6
block_num = 0
task_blocks = 0

#looping through blocks
while block_num < block_count :
    folder_index = block_num
    check_escape()
    folder = custom_folder_order[folder_index]
    #task vs control code (trigger 1)
    
    ctrl = False
    if folder == 'control' :
        ctrl = True
        condition = 1
        if info['Participant #'] == '1' :
            i = 1
            folder = get_control_folder(block_num, i, folder)
        elif info['Participant #'] == '2' :
            i = -1
            folder = get_control_folder(block_num, i, folder)
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
        #Assigning trigger codes
        #which folder is being used (trigger 2)
        folder_code = folder_code_dict[folder]
        #role code (trigger 3)
        role_code = 1 if role == 'director' else 2
        #first vs repeat block (trigger 4)
        repeat = 1 if i == 0 else 2
        
        #Generating triggers
        cond_trig = condition + 10
        fold_trig = folder_code + 20
        role_trig = role_code + 30
        rep_trig = repeat + 40
        
        outlet.push_sample(x=[77])
        show_fixation()
        
        outlet.push_sample(x=[66])
        show_instructions(role, ctrl)
        
        outlet.push_sample(x=[cond_trig])
        outlet.push_sample(x=[fold_trig])
        outlet.push_sample(x=[role_trig])
        outlet.push_sample(x=[rep_trig])
        print(cond_trig, fold_trig, role_trig, rep_trig)
        
        if role == 'guessor':
            guessor_block(block_num + 1, ctrl, folder, images)
        else:
            director_block(block_num + 1, ctrl, folder, images)
            
        role = 'director' if role == 'guessor' else 'guessor'
    
    block_num += 1

## For the end of the task
thanks.draw()
outlet.push_sample(x=[99])
print(99)
win.flip()
core.wait(5)
win.close()
core.quit()
