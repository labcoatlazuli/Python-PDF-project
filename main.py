from PyPDF2 import PdfWriter, PdfReader
import tkinter as tk
from tkinter import StringVar, ttk
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import tkinter.filedialog as fd
from collections import OrderedDict
import pdfprocess

from os import path as path

root = tk.Tk()

# Window Setup:
root.title('Exam Booklet A3 - Scanned PDF Auto-Processor v0.1 - St Dunstan\'s College - Author: Eugene Lee')

window_width = 960
window_height = 600

# get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# find the center point
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

# set the position of the window to the center of the screen
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

root.minsize(960, 280)
# root.attributes('-topmost', True)
root.attributes('-alpha', 1)

root.columnconfigure(0, minsize= 500)
root.columnconfigure(1, weight= 1)
root.rowconfigure(0, minsize=315)
root.rowconfigure(1, minsize=50)
root.rowconfigure(3, weight=1, minsize=100)

# Main Program variables

list_filenames = []
DEFAULT_FILE_SUFFIX = '_A4processed'
export_location: str = ''

# Options frame
options = ttk.LabelFrame(root, text='Options')
options['padding'] = 5
options['relief'] = 'solid'
options.grid(row=0,column=0, padx=5, pady=5, sticky='NEW')




# -------------------------------------------------------------SELECT FILES---------------------------------------------------------------

# Select Files Frame
select_frame = ttk.Frame(options)
select_frame['padding'] = 20
select_frame.grid(row=0, column=0, sticky='EW')


# 1. Select files Label
select_status_label = ttk.Label(
    select_frame, 
    text="1.\tSelect the files you wish to transform. \nHold Shift (or Ctrl) to select multiple (individual) files.".expandtabs(4),
    font=("Helvetica", 14),
    
)
select_status_label.grid(row=0, column=0, sticky="W",)

select_status_info_text = StringVar(value='Please add some files to the list for processing')
select_status_info_label = ttk.Label(
    select_frame,
    textvariable=select_status_info_text,
    font=('Helvetica', 9),
    justify=tk.LEFT
)
select_status_info_label.grid(row=1, column=0, sticky='W')

# update text in info
def update_filecount_info():

    global select_status_info_text, list_filenames
    if len(list_filenames) > 0:
        select_status_info_text.set(value=f'{len(list_filenames)} PDFs currently in list')
        select_status_info_label.config(foreground='green')
    else:
        select_status_info_text.set(value='Please add some files to the list for processing')
        select_status_info_label.config(foreground='red')

    update_start_btn_clickable()


# 1.5 Select files button
def select_files_pressed():
    filenames = fd.askopenfilenames(
        parent=root, 
        title='Select PDFs: Shift+Click or Ctrl+Click for multiple files', filetypes=(("PDF Files", "*.pdf"),)
    )

    global list_filenames
    list_filenames = list_filenames + list(filenames)

    update_file_tree()
    update_filecount_info()

select_files_btn = ttk.Button(options, 
    text='Add files to list',
    
    command=select_files_pressed,
    padding=10
    )

select_files_btn.grid(row=0, column=1, sticky='EW', padx=5, pady=5)


        
# -------------------------------------------------------------SUFFIX ENTRY---------------------------------------------------------------

# Suffix entry text Frame
suffix_frame = ttk.Frame(options)
suffix_frame['padding'] = 20
suffix_frame.grid(row=1, column=0, sticky='W')


# 2. Suffix Entry Label
suffix_label = ttk.Label(
    suffix_frame, 
    text="2.\tChoose a suffix to denote processed files.".expandtabs(4),
    font=("Helvetica", 14),
    justify=tk.LEFT,
)
suffix_label.grid(row=0, column=0, sticky='W')

# Set default suffix

suffix_from_entry = StringVar(value=DEFAULT_FILE_SUFFIX)

# 2.3 Suffix status info label
suffix_status_info_text = StringVar(value=f'Example output: A3scannedTestPaper{suffix_from_entry.get()}.pdf')
suffix_status_info_label = ttk.Label(
    suffix_frame,
    textvariable=suffix_status_info_text,
    font=('Helvetica', 9),
    justify=tk.LEFT
)
suffix_status_info_label.grid(row=1, column=0, sticky='W')

suffix_entry = ttk.Entry(
    options,
    textvariable = suffix_from_entry
)

suffix_entry.grid(row=1, column=1, sticky='EW', padx=5, pady=5, ipadx=10)

# update text in info
def update_entry_info(event):

    print("new suffix_from_entry is " + suffix_from_entry.get())

    global suffix_status_info_text
    if suffix_from_entry.get() != '':
        suffix_status_info_text.set(value=f'Example output: A3scannedTestPaper{suffix_from_entry.get()}.pdf')
        suffix_status_info_label.config(foreground='green')
    else:
        suffix_status_info_text.set(value='Please enter a suffix')
        suffix_status_info_label.config(foreground='red')
    update_start_btn_clickable()


suffix_entry.bind('<Any-KeyRelease>', update_entry_info)

# -------------------------------------------------------------TREEVIEW---------------------------------------------------------------

record = dict()

# Tree frame
tree_frame = ttk.LabelFrame(root, text='Selected Files', width= 500,)
tree_frame['padding'] = 5
tree_frame['relief'] = 'solid'
tree_frame.grid(row = 0,rowspan=3, column=1, padx=5, pady=5, sticky='NSEW', ipadx=5, ipady=5)
tree_frame.columnconfigure(0, weight=1)
tree_frame.columnconfigure(1, minsize=20)
tree_frame.rowconfigure(0, weight=1)
tree_frame.rowconfigure(1, minsize=20)


# Setup File Treeview
tree_columns = ('Filename')
file_tree = ttk.Treeview(tree_frame, columns=tree_columns, show='headings')
file_tree.heading('Filename', text='Filename')
file_tree.grid(row = 0, column=0, padx=5, pady=5, sticky='NSEW',)

scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=file_tree.yview)
file_tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky='nes', pady=5)

# Update the tree view

def update_file_tree():
    for i in file_tree.get_children():
        file_tree.delete(i)
    global list_filenames
    list_filenames = list(OrderedDict.fromkeys(list_filenames))
    for filename in list_filenames:
        file_tree.insert('', tk.END, values=filename.replace(" ", '\ '))
    update_start_btn_clickable()

# Delete selected files
def delete_selected(event):
    print(file_tree.selection())
    global list_filenames
    for selected_item_ref in file_tree.selection(): # selection returns references to each row
        item = file_tree.item(selected_item_ref) # fetch item object
        item_text = item['values'][0]
        print(item_text)

        list_filenames.remove(item_text.replace('\ ', ' '))

    update_file_tree()
    update_filecount_info()
    
    print(list_filenames)

# Setup delete file button

delete_file_btn = ttk.Button(
    tree_frame,
    text= 'Remove from list',
    state='disabled',
    command=lambda: delete_selected(event=None),
    padding=2

)
delete_file_btn.grid(row=1, sticky='EW', padx=4)

# Setup alternate bindings
file_tree.bind('<Delete>', delete_selected)
file_tree.bind('<BackSpace>', delete_selected)


# Files selected in tree event listener
selected_files = []
def item_selected(event):
    #enable remove file from list button
    delete_file_btn.config(state='enabled')
    global selected_files


def item_deselected(event):
    delete_file_btn.config(state='disabled')

file_tree.bind('<<TreeviewSelect>>', item_selected)
file_tree.bind('<<TreeviewDeselect>>', item_deselected)




# -------------------------------------------------------------EXPORT FOLDER---------------------------------------------------------------

# Export Folder Frame
export_frame = ttk.Frame(options)
export_frame['padding'] = 20
export_frame.grid(row=2, column=0, sticky='W')

# 3. Export location Label
export_label = ttk.Label(
    export_frame,
    text="3.\tChoose an output folder - processed PDFs will go here".expandtabs(4),
    font=("Helvetica", 14),
    justify=tk.LEFT,
    

)
export_label.grid(row=0, column=0, sticky='W')

export_status_info_text = StringVar(options, value='Export folder not set'.expandtabs(4))

# 3.7 Export status info label underneath
export_status_info_label = ttk.Label(
    export_frame,
    textvariable=export_status_info_text,
    font=("Helvetica", 9),
    justify=tk.LEFT
    
)
export_status_info_label.config(foreground='red')
export_status_info_label.grid(row=1, column=0, sticky='W')

# 3.5 Export location button

def export_location_pressed():
    global export_location, export_status_info_text
    export_location = fd.askdirectory(
        parent=root, 
        title='Select export folder'
    )
    
    if export_location != '':
        print(export_location + ' hello')
        export_status_info_text.set(value=f'Exporting to {export_location}')
        export_status_info_label.config(foreground='green')
    else:
        export_status_info_text.set(value=f'Export folder not set')
        export_status_info_label.config(foreground='red')
    update_start_btn_clickable()
        
export_location_btn = ttk.Button(options, 
    text='Select folder', 
    command=export_location_pressed,
    padding=10
    )

export_location_btn.grid(row=2, column=1, sticky='EW', padx=5, pady=5)

# -------------------------------------------------------------Start Button---------------------------------------------------------------

def update_start_btn_clickable():
    if list_filenames != [] and export_location != '' and suffix_from_entry.get() != '':
        start_btn.config(state='enabled')
    else:
        start_btn.config(state='disabled')

def start_pressed():

    global list_filenames

    for filename in list_filenames:
        # Remove extension first
        path_filename = Path(filename).with_suffix('')

        basename = path.basename(path_filename)
        basename = basename + suffix_from_entry.get()
        file_extension = '.pdf'
        destination_path = path.join(export_location, basename + file_extension)

        try:
            pdfprocess.split_pages(filename, destination_path)
            log(f'Successfully processed {filename} to {destination_path}')
        except pdfprocess.OddPagesException:
            log(f'Couldn\'t process {filename}: Odd number of pages detected')


    
    list_filenames = []

    update_file_tree()
    update_filecount_info()
    update_start_btn_clickable



start_btn = ttk.Button(
    root,
    text='Start!',
    padding=20,
    state='disabled',
    command=start_pressed

)

start_btn.grid(row=1, column=0, sticky='NEWS', padx=10, pady=10, )

# -------------------------------------------------------------Logging window---------------------------------------------------------------

log_LabelFrame = ttk.LabelFrame(
    root,
    text='Log'

)

log_LabelFrame['padding'] = 20
log_LabelFrame.grid(row=3, column=0,columnspan=4, sticky='NSEW', padx=5, pady=5)

log_scrolltext = ScrolledText(log_LabelFrame)
log_scrolltext.pack(fill=tk.BOTH)
log_scrolltext.config(state='disabled')

def log(msg: str) -> None:
    log_scrolltext.config(state='normal')
    log_scrolltext.insert(tk.INSERT, chars=str(msg + '\n'))
    log_scrolltext.config(state='disabled')

# -------------------------------------------------------------Main---------------------------------------------------------------

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()

# reader = PdfReader('example.pdf')
# writer =  PdfWriter
