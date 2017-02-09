import Tkinter, Tkconstants, tkFileDialog, os
import tkMessageBox
from patcher import patch
from rominfo import common_filenames

class TkFileDialogExample(Tkinter.Frame):

    def __init__(self, root):

        Tkinter.Frame.__init__(self, root)

        # define buttons
        Tkinter.Label(self, text="User Disk").grid(row=0, column=0, sticky='E')
        Tkinter.Label(self, text="Disk B1").grid(row=1, column=0, sticky='E')
        Tkinter.Label(self, text="Disk B2").grid(row=2, column=0, sticky='E')
        Tkinter.Label(self, text="Disk B3").grid(row=3, column=0, sticky='E')
        Tkinter.Label(self, text="Disk B4").grid(row=4, column=0, sticky='E')


        diskA = Tkinter.StringVar()
        diskB2 = Tkinter.StringVar()
        diskB3 = Tkinter.StringVar()
        diskB4 = Tkinter.StringVar()


        AEntry = Tkinter.Entry(self, textvariable=diskA)
        B1Entry = Tkinter.Entry(self)
        B1Entry.insert(0, 'Patch not needed')
        B1Entry['state'] = 'disabled'
        B2Entry = Tkinter.Entry(self, textvariable=diskB2)
        B3Entry = Tkinter.Entry(self, textvariable=diskB3)
        B4Entry = Tkinter.Entry(self, textvariable=diskB4)

        AEntry.grid(row=0, column=1)
        B1Entry.grid(row=1, column=1)
        B2Entry.grid(row=2, column=1)
        B3Entry.grid(row=3, column=1)
        B4Entry.grid(row=4, column=1)

        # TODO: If I set these to attributes, it will probably cut down on all the argument passing I'm doing
        all_entry_text = [diskA, diskB2, diskB3, diskB4]
        B_entries = [B2Entry, B3Entry, B4Entry]

        ABrowse = Tkinter.Button(self, text='Browse...', command= lambda: self.askopenfilenamediskA(diskA, all_entry_text, B_entries, PatchBtn))
        B2Browse = Tkinter.Button(self, text='Browse...', command= lambda: self.askopenfilename(diskB2, all_entry_text, PatchBtn))
        B3Browse = Tkinter.Button(self, text='Browse...', command= lambda: self.askopenfilename(diskB3, all_entry_text, PatchBtn))
        B4Browse = Tkinter.Button(self, text='Browse...', command= lambda: self.askopenfilename(diskB4, all_entry_text, PatchBtn))

        ABrowse.grid(row=0, column=2)
        B2Browse.grid(row=2, column=2)
        B3Browse.grid(row=3, column=2)
        B4Browse.grid(row=4, column=2)

        PatchBtn = Tkinter.Button(self, text="Patch", command= lambda: self.patchfiles(diskA, diskB2, diskB3, diskB4))
        PatchBtn.grid(row=5, column=5)
        PatchBtn['state'] = 'disabled'

        Console = Tkinter.Text(self, height=3, width=30)
        Console.grid(row=5, column=1,) # TODO: Use columnspan to do something sane with it

        # define options for opening or saving a file
        self.file_opt = options = {}
        options['defaultextension'] = '.fdi'
        options['filetypes'] = [('PC-98 images', ('.fdi', '.hdm', '.hdi')), ('all files', '.*')]
        options['initialdir'] = os.path.abspath(os.path.curdir)
        options['initialfile'] = 'myfile.txt'
        options['parent'] = root
        options['title'] = 'Select a disk image'

        # defining options for opening a directory
        self.dir_opt = options = {}
        options['initialdir'] = os.path.curdir
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

        self.toggleDiskBFields(filename, B_entries, patchbtn)

    def askopenfilename(self, field, all_entry_text, patchbtn):
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        field.set(filename)
        self.checkCommonFilenames(all_entry_text)

        if all([t.get() for t in all_entry_text]):
            patchbtn['state'] = 'normal'
        else:
            patchbtn['state'] = 'disabled'

    def checkCommonFilenames(self, all_entry_text):
        if sum([len(t.get()) > 0 for t in all_entry_text]) == 1:
            filepath = [t.get() for t in all_entry_text if len(t.get()) > 0][0]
            file_folder = '/'.join(filepath.split('/')[:-1]) + '/'
            filename = filepath.split('/')[-1]
            for c in common_filenames:
                if filename in c:
                    for i, disk in enumerate(c):
                        if disk in os.listdir(file_folder):
                            disk_filepath = file_folder + disk
                            all_entry_text[i].set(disk_filepath)
                    return None

    def toggleDiskBFields(self, diskAFilename, B_entries, patchbtn):
        if diskAFilename.split('.')[-1] == 'hdi':
            print "it's an HDI"
            for b in B_entries:
                b['state'] = 'disabled'
            patchbtn['state'] = 'normal'
        elif all(B_entries):
            patchbtn['state'] = 'normal'
        else:
            for b in B_entries:
                b['state'] = 'normal'
            patchbtn['state'] = 'disabled'


    def patchfiles(self, A, B2, B3, B4):
        print A.get(), B2.get(), B3.get(), B4.get()
        diskA = A.get()
        if diskA.split('.')[-1].lower() == 'hdi':
            print "it's an HDI again"
            success = patch(diskA)
        else:
            success = patch(diskA, B2.get(), B3.get(), B4.get())
            
        if success:
            tkMessageBox.showinfo('Patch successful!', 'Go play it now.')
        else:
            tkMessageBox.showerror('Error', 'Whoops, something went wrong.')


if __name__=='__main__':
    root = Tkinter.Tk()
    root.title('E.V.O.: The Theory of Evolution Patcher')
    root.geometry('400x200')
    TkFileDialogExample(root).pack()
    root.mainloop()