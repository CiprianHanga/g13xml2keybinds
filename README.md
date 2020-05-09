# g13xml2keybinds
I needed something to parse the xml profiles created by Logitech's G13 Gaming Software on Windows.
This converts what it can to a bindfile that works with g13d (https://github.com/khampf/g13) on 
Arch Linux (https://wiki.archlinux.org/index.php/Logitech_G13) (originally, but it should be OS agnostic). 

I call it using xargs, but it's designed to take one profile at a time and process it.

Example:
g13xml2keybinds.py <profile location> <shiftstate>

to get shiftstate "2" (see the xml file you provide for the tag "shiftstate") of the below profile:
g13xml2keybinds.py profiles/\{4A37C232-D60F-4D01-92D2-BEBD24C87CF4\}.xml 2

or with xargs:
find . -type f -iname "*.xml" -print0 | xargs -I {} -0 ./g13xml2keybinds.py "{}" 2

It is what it is. Feel free to edit it to your liking. No warranty. There's a brief help dialog (-h). 
Designed on python 3.8.2.

A shiftstate is bound to one of three M# buttons on the top of the G13 (next to a fourth MR button). 
Unfortunately, the g13d doesn't appear to support using three profiles at once, so the script gives 
the opportunity to export the three shiftstates into one bindfile each. You can probably script 
around that limitation somehow, just haven't figured out a way yet.

Example bindfile: https://github.com/zekesonxx/g13-profiles/blob/master/default.bind
