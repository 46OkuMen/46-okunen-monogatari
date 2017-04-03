import Tkinter, Tkconstants, tkFileDialog
import sys
import time
from os import listdir, getcwd, chdir
from os import path as ospath
from ttk import *
import tkMessageBox
from patcher import patch
from rominfo import common_filenames
from romtools.disk import HARD_DISK_FORMATS

# TODO: Enter to press the "Patch" button.
# TODO: Use a labelframe to clean things up a bit?

class PatcherGUI(Tkinter.Frame):

    def __init__(self, root):

        Tkinter.Frame.__init__(self, root)

        Label(self, text="E.V.O.: The Theory of Evolution, English Translation by 46 OkuMen")
        # define buttons
        Label(self, text="HDI/User Disk").grid(row=1, column=0, sticky='E')
        Label(self, text="Disk B1").grid(row=2, column=0, sticky='E')
        Label(self, text="Disk B2").grid(row=3, column=0, sticky='E')
        Label(self, text="Disk B3").grid(row=4, column=0, sticky='E')
        Label(self, text="Disk B4").grid(row=5, column=0, sticky='E')
        #for i, d in enumerate(DISKS):
        #    Label(self, text='Disk ' + d).grid(row=i, column=0, sticky='E')

        diskA = Tkinter.StringVar()
        diskB2 = Tkinter.StringVar()
        diskB3 = Tkinter.StringVar()
        diskB4 = Tkinter.StringVar()
        self.PatchStr = Tkinter.StringVar()
        self.PatchStr.set('Patch')

        AEntry = Entry(self, textvariable=diskA)
        B1Entry = Entry(self)
        B1Entry.insert(0, 'Patch not needed')
        B1Entry['state'] = 'disabled'
        B2Entry = Entry(self, textvariable=diskB2)
        B3Entry = Entry(self, textvariable=diskB3)
        B4Entry = Entry(self, textvariable=diskB4)

        AEntry.grid(row=1, column=1, padx=5)
        B1Entry.grid(row=2, column=1, padx=5)
        B2Entry.grid(row=3, column=1, padx=5)
        B3Entry.grid(row=4, column=1, padx=5)
        B4Entry.grid(row=5, column=1, padx=5)

        # TODO: If I set these to attributes, it will probably cut down on all the argument passing I'm doing
        all_entry_text = [diskA, diskB2, diskB3, diskB4]
        B_entries = [B2Entry, B3Entry, B4Entry]
        self.advanced_active = Tkinter.BooleanVar(False)

        ABrowse = Button(self, text='Browse...', command= lambda: self.askopenfilenamediskA(diskA, all_entry_text, B_entries, self.PatchBtn))
        B2Browse = Button(self, text='Browse...', command= lambda: self.askopenfilename(diskB2, all_entry_text, B_entries, self.PatchBtn))
        B3Browse = Button(self, text='Browse...', command= lambda: self.askopenfilename(diskB3, all_entry_text, B_entries, self.PatchBtn))
        B4Browse = Button(self, text='Browse...', command= lambda: self.askopenfilename(diskB4, all_entry_text, B_entries, self.PatchBtn))

        ABrowse.grid(row=1, column=2, padx=5)
        B2Browse.grid(row=3, column=2, padx=5)
        B3Browse.grid(row=4, column=2, padx=5)
        B4Browse.grid(row=5, column=2, padx=5)

        self.PatchBtn = Button(self, textvariable=self.PatchStr, command= lambda: self.patchBtnCommand(diskA, diskB2, diskB3, diskB4, pathInDisk))
        self.PatchBtn.grid(row=7, column=5)
        self.PatchBtn['state'] = 'disabled'

        AdvancedBtn = Button(self, text="Advanced...", command= lambda: self.toggleadvanced(AdvancedPath, AdvancedLabel))
        AdvancedBtn.grid(row=7, column=2)

        pathInDisk = Tkinter.StringVar('')
        AdvancedPath = Entry(self, textvariable=pathInDisk)
        AdvancedLabel = Label(self, text="Path In Disk")

        # define options for opening or saving a file
        self.file_opt = options = {}
        options['defaultextension'] = '.fdi'
        options['filetypes'] = [('PC-98 images', ('.fdi', 'fdd', '.hdm', '.hdi', 'd88')), ('all files', '.*')]
        options['initialdir'] = exe_dir
        options['initialfile'] = 'myfile.txt'
        options['parent'] = root
        options['title'] = 'Select a disk image'

        # defining options for opening a directory
        self.dir_opt = options = {'initialdir': exe_dir}
        options['initialdir'] = exe_dir
        options['mustexist'] = False
        options['parent'] = root
        options['title'] = 'Select a disk image'

    def askopenfilenamediskA(self, field, all_entry_text, B_entries, patchbtn):

        """Returns an opened file in read mode.
        This time the dialog just returns a filename and the file is opened by your own code.
        """

        # get filename
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        field.set(filename)

        self.checkCommonFilenames(all_entry_text)

        self.toggleDiskBFields(filename, B_entries, self.PatchBtn)

    def askopenfilename(self, field, all_entry_text, B_entries):
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        field.set(filename)
        self.checkCommonFilenames(all_entry_text)

        if all([t.get() for t in all_entry_text]):
            self.PatchBtn['state'] = 'normal'
        else:
            self.PatchBtn['state'] = 'disabled'

        print "Calling toggleDiskBFields"
        self.toggleDiskBFields(filename, B_entries, self.PatchBtn)

    def checkCommonFilenames(self, all_entry_text):
        if sum([len(t.get()) > 0 for t in all_entry_text]) == 1:
            filepath = [t.get() for t in all_entry_text if len(t.get()) > 0][0]
            file_folder = '/'.join(filepath.split('/')[:-1]) + '/'
            filename = filepath.split('/')[-1]
            for c in common_filenames:
                if filename == c[0]:
                    for i, disk in enumerate(c):
                        if disk in listdir(file_folder):
                            disk_filepath = file_folder + disk
                            all_entry_text[i].set(disk_filepath)
                    return None

    def toggleDiskBFields(self, diskAFilename, B_entries, patchbtn):
        if diskAFilename.split('.')[-1] in HARD_DISK_FORMATS:
            for b in B_entries:
                b['state'] = 'disabled'
            self.PatchBtn['state'] = 'normal'
        elif all([b.get() for b in B_entries]):
            print [b.get() for b in B_entries]
            print "All B entries are filled in"
            for b in B_entries:
                b['state'] = 'normal'
            self.PatchBtn['state'] = 'normal'
        else:
            print "Setting the B entries back to normal"
            for b in B_entries:
                b['state'] = 'normal'
            self.PatchBtn['state'] = 'disabled'


    def patchfiles(self, A, B2, B3, B4, path=None):
        backup = ospath.join(exe_dir, 'backup')

        diskA = A.get()
        if diskA.split('.')[-1].lower() in HARD_DISK_FORMATS:
            if self.advanced_active.get():
                result = patch(diskA, path_in_disk=path.get(), backup_folder=backup)
            else:
                result = patch(diskA, backup_folder=backup)
        else:
            result = patch(diskA, B2.get(), B3.get(), B4.get(), backup_folder=backup)
            
        self.patchBtnIdle()
        if not result:
            print "Patching was successful"
            tkMessageBox.showinfo('Patch successful!', 'Go play it now.')
        else:
            print "Error while patching:", result
            tkMessageBox.showerror('Error', 'Error: ' + result)

        

    def patchBtnCommand(self, A, B2, B3, B4, path=None):
        self.patchBtnPatching()
        self.update_idletasks() # Necessary to get the button text to update
        self.patchfiles(A, B2, B3, B4, path)


    def patchBtnPatching(self):
        self.PatchStr.set('Patching...')
        self.PatchBtn['state'] = 'disabled'


    def patchBtnIdle(self):
        print "Editing patchstr and patchbtn now"
        self.PatchStr.set('Patch')
        self.PatchBtn['state'] = 'normal'

    def toggleadvanced(self, advpath, advlabel):
        print "advanced_active:", self.advanced_active.get()
        if self.advanced_active.get():
            root.geometry('400x160')
            advpath.grid_forget()
            advlabel.grid_forget()
            self.advanced_active.set(False)
        else:
            root.geometry('400x180')

            advpath.grid(row=6, column=1)
            advlabel.grid(row=6, column=0, sticky='E')
            self.advanced_active.set(True)

if __name__=='__main__':
    exe_dir = getcwd()
    if hasattr(sys, '_MEIPASS'):
        chdir(sys._MEIPASS)

    logfilename = ospath.join(exe_dir, 'evo-patch-log.txt')
    sys.stderr = sys.stdout = open(logfilename, 'w', 0)
    print "\n", time.ctime(time.time())

    root = Tkinter.Tk()
    root.title('E.V.O.: The Theory of Evolution Patcher')
    root.iconbitmap('46.ico')
    root.geometry('400x160')
    PatcherGUI(root).pack()
    root.mainloop()

# TODO: Handle unicode filenames/filepaths.
    # Appears to be a bug in python 2.7 subprocess that they won't fix. Should I do 2to3?
    # Used an error message for now
