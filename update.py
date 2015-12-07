# Things that need automation:
#
# 1) Update and launch.
# Open up the disk A rom.
# Press enter.
# Drag in whatever files have been edited.
# Close the program.
# Open up anex86.
# Hit enter.
# (does anex86 need to update the roms used, or does it keep just the location each time?)
# Hit start.
#
# 2) WindHex32 settings.
# Open up WindHex32.
# Open -> Table File -> Table #1.
# Up one level.
# Select shinkaron.tbl.
# Press enter.
# Press Ctrl-D (view data as unicode).

from pywinauto import application
import os

app = application.Application()
app.Start_("WindHex32\WindHex32.exe")
app.WindHex.DrawOutline() # Could not find WindHex in []