# Rio_Intergation
These files are for testing the communications between the Raspberry Pi and RoboRio. 
The "gearvision" files are written in Python and reside on a Raspberry Pi. 
The file called Networktable_Sample_Code is C++ code that is complied via Eclipse and goes on the Roborio.
A custom dashboard is needed to display this information also. 

Here is a brief explanation of how this works.

Networktables allow multiple devices to share data. Devices do not need to use the same lanugauge which is very convinient. There are 3 parts to make this work. This is how team #2040 is approacing the 2017 game
1) Vision is processed on a Raspberry Pi using Python and OpenCV - straight hand code and not using GRIP. 
2) C++ robot code. This code is an example of what is needed to make the Networktables work, It is NOT a complete robot program.
3) Dashboard GUI to read the networktables. 

How it works:

The Pi places variables to the networktable via the pynetworktables library. Values for error(from center of screen), target status, etc are put on the table. The mechanics of vision processing are a separate topic. Look at python code example at other parts of this site for examples.
The C++ program defines the EXACT same variables by initializing them and setting the type (double, boolean) Lines 28-51
Then the C++ code "GETS" the number from the table. Lines 106-118
Lines 129-130 will place the numbers in the first two "DB" rows in the "Basic" tab. This is OK for testing but there are no labels.
Lines 131-138 put the variables in a place where the NT Read blocks can read them. 

Dashboard set-up in a few words. 

You need to know enough about Labview to open the DASHBOARD project and edit it. If Labview is totally foreign, there are a few youtube videos that can help. https://www.youtube.com/channel/UC_d8aqPvnhXtA9cLbg_KXOQ and https://www.youtube.com/channel/UCSqphwQmX1iwQeH5Tizyfzw 
Start by going to the WPI library and locating the the block with and "NT" on it. Choose the NT with the image of pair of glasses on it. This is the read NT block. Create a constant at the NT read input. The name needs to be exactly the same as the variable found in the C++ code, which is the same as the variables in the Python code. Next connect the output of the NT read block to an indicator, meter, or graph. Then customize as you like.
