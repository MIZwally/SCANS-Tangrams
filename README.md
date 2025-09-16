<strong>Tangrams</strong>

This task involves 2 participants and 2 roles (director and guessor). Each participant is assigned a number, either 1 or 2, which determines their initial role. This script can be run for both participants at the same time with the input of their number.

The goal of the task is for the guessor to correctly guess which image, or "tangram," the director is describing. The guessor sees 6 different tangrams and the director sees 1 at a time, rotating through and describing each of the 6 images that the guessor sees. After one round, the roles switch; the director becomes the new guessor while the guessor becomes the new director. The images do not change with the role switch, so the new director is now describing the images that they were guessing between, and the new guessor is guessing from the images that they just described.

Each iteration of this pattern is considered a block, with the set of tangrams changing for each block. There are 2 types of blocks: task blocks and control blocks. Task blocks are as explained above, and can be either easy or hard. Easy tangrams are generally easier to describe than harder tangrams, and an easy block is always followed by a hard block. For the control blocks, the director and guessor do not see the same set of tangrams, so the director will be explaining different tangrams than the set that the guessor can choose from.

Our paradigm contains 4 task blocks (2 pairs of easy and hard blocks) and 2 control blocks, with the order randomly preassigned with counterbalanced via a 3 letter "run order code." Each code corresponds to a combination of 2 blocks. For the task condition, each code is a pair of easy/hard blocks, while 

<strong>Run Order Code Interpretation:</strong>

<ins>Task Condition</ins>

C: easyA,hardA &emsp;&emsp;&emsp;&emsp; 
G: easyB,hardA &emsp;&emsp;&emsp;&emsp; 
K: easyC,hardA &emsp;&emsp;&emsp;&emsp;&nbsp; O: easyD,hardA\
D: easyA,hardB &emsp;&emsp;&emsp;&emsp; 
H: easyB,hardB &emsp;&emsp;&emsp;&emsp; 
L: easyC,hardB &emsp;&emsp;&emsp;&emsp;&nbsp;&nbsp; P: easyD,hardB\
E: easyA,hardC &emsp;&emsp;&emsp;&emsp;&nbsp;
I: easyB,hardC &emsp;&emsp;&emsp;&emsp;&nbsp;
M: easyC,hardC &emsp;&emsp;&emsp;&emsp; Q: easyD,hardC\
F: easyA,hardD &emsp;&emsp;&emsp;&emsp;
J: easyB,hardD &emsp;&emsp;&emsp;&emsp;&nbsp;
N: easyC,hardD &emsp;&emsp;&emsp;&emsp;&nbsp; R: easyD,hardD

<ins>Control Condition</ins>\
W: controlA,controlC\
X: controlA,controlD\
Y: controlB,controlC\
Z: controlB,controlD

To avoid repeating tangrams, only certain task codes can be paired together in one run order code: K can only be paired with N, and L can only be paired with M. An example run order code would be "KWN". This code would indicate that the session would have 2 task blocks, then 2 control blocks, then 2 more task blocks from a different set of tangrams.

This task is designed to be used with fNIRS technology, so Lab Streaming Layer (LSL) triggers are embedded into the code to mark the data at different events. Each block will have 6 triggers, with each trigger type occuring twice. First there will be a fixation trigger for the fixation period, followed by an instructions triggern for the instructions window, then a run trigger for the round of the tangrams task. The run triggers change depending on the block type (task or control), the set of tangrams (easy vs hard, A vs B), whether the participant role is director or guessor, and whether or not this is the first round or a second round in a block. Each of these variables is part of a series of back-to-back triggers, with the first digit indicating which trigger it is, and the second digit being the actual value to encode.

Condition - value + 10 (11 for control, 12 for task)
Folder - value + 20 (ex: 23)
Role - value + 30 (31 for director, 32 for guessor)
Repeat - value + 40 (41 for first iteration, 42 for second)

There are are other triggers, such as the fixation and instructions triggers, that are static in value. See below for those triggers and their values.

<strong> Static Triggers:</strong>

0 - start of experiment\
66 - fixation\
77 - instructions\
99 - end of experiment