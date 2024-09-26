from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk, ImageEnhance
from typing import Literal
import os
import getpass
import re

# get main path
__BASE_DIR__ = os.path.dirname( os.path.abspath( __file__ ) )

class Application(Tk):

    def __init__(self):
        # initialization
        super().__init__()
        # size window
        self.__width = 340
        self.__height = 700
        self.position_x = (self.winfo_screenwidth() - self.__width) / 2
        self.position_y = (self.winfo_screenheight() - self.__height) / 2
        self.geometry("%dx%d+%d+%d" % (self.__width, self.__height, self.position_x, self.position_y))
        # disabled maxmium window
        self.resizable(False, False)
        # title
        self.title("Watermark")
        # icon bar
        self.__icon_bar = os.path.join( __BASE_DIR__, "assets/icons/watermark.ico" )
        self.iconbitmap(self.__icon_bar)
        # window background and padding
        self.configure(padx=22, background="#ebeced")
        # styles
        self.style = ttk.Style(self)
        # theme
        self.style.theme_use("clam")
        # style -> buttons
        self.style.configure("TButton", font=(None, 15))
        # design
        self.setDesign()
        ############## variables
        # get watermark from canvas
        self.watermark_id = None
        # get path watermark
        self.watermark_path = None
        # mode
        self.lock_mode = False
    
    def setDesign(self):
        # frame -> content 'canvas'
        self.frame_canvas = ttk.Frame(self)
        self.frame_canvas.pack(pady=15, fill=X)
        # canvas -> display icon
        self.canvas = Canvas(self.frame_canvas, bg="#000", cursor="hand2", highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True)
        # canvas event
        self.canvas.bind("<Button-1>", self.selectIcon)
        # canvas background
        self.background = PhotoImage(file=os.path.join(__BASE_DIR__, "assets/canvas.png"))
        self.canvas.create_image(0,0,anchor=NW, image=self.background)
        # label -> opacity icon
        self.lbl_opacity_icon = Label(self, text="Opacity: 250", anchor=W, bg=self.cget("bg"))
        self.lbl_opacity_icon.pack(fill=X)
        # value scale -> opacity icon
        self.value_opacity_icon = IntVar(value=250)
        # spinbox -> opacity icon
        self.sc_opacity_icon = ttk.Scale(self, orient="horizontal", from_=10, to=250, variable=self.value_opacity_icon,
                                         command=self.setOpacityIcon, state="disabled")
        self.sc_opacity_icon.pack(fill=X)
        # label -> type
        self.lbl_type = Label(self, text="Type", anchor=W, bg=self.cget("bg"))
        self.lbl_type.pack(fill=X, pady=(10,0))
        # combobox -> type
        self.value_types = ["Icon", "Image"]
        self.cbx_type = ttk.Combobox(self, value=self.value_types, state="readonly", justify=CENTER)
        self.cbx_type.pack(fill=X)
        # set icon default
        self.cbx_type.current(0)
        # event combobox 'type'
        self.cbx_type.bind("<<ComboboxSelected>>", self.setType)
        # label -> size icon
        self.lbl_size_icon = Label(self, text="Size", anchor=W, bg=self.cget("bg"))
        self.lbl_size_icon.pack(fill=X, pady=(10,0))
        # value spinbox -> size icon
        self.value_size_icon = IntVar(value=75)
        # register
        self.reg = self.register(self.callback_number)
        # spinbox -> size icon
        self.sp_size_icon = ttk.Spinbox(self, from_=25, to=256, state="disabled", justify=CENTER, textvariable=self.value_size_icon,
                                        command=self.resizeIcon, validate="key", validatecommand=(self.reg, "%P"))
        self.sp_size_icon.pack(fill=X)
        # frame -> alert 
        self.frame_alert = Frame(self)
        self.frame_alert.pack(fill=X)
        # label -> alert
        self.lbl_alert = Label(self.frame_alert, text="● maximum size '1920'\n● Field must be non-blank", anchor=W,
                               justify=LEFT, bg=self.cget("bg"), font=(None, 10), fg="#f00")
        # label -> folder image
        self.lbl_folder_images = Label(self, text="Folder Images", anchor=W, bg=self.cget("bg"))
        self.lbl_folder_images.pack(fill=X, pady=(10,0))
        # value entry -> folder images
        self.value_folder_images = StringVar()
        # entry -> folder image
        self.ent_folder_images = ttk.Entry(self, justify=CENTER, state="disabled", cursor="arrow", textvariable=self.value_folder_images)
        self.ent_folder_images.pack(fill=X)
        # event entry 'folder images'
        self.ent_folder_images.bind("<Button-1>", self.selectFolderImages)
        # label -> output
        self.lbl_output = Label(self, text="Output", anchor=W, bg=self.cget("bg"))
        self.lbl_output.pack(fill=X, pady=(10,0))
        # value entry -> output
        self.value_output = StringVar(value=f"C:\\Users\\{getpass.getuser()}\\Pictures")
        # entry -> output
        self.ent_output = ttk.Entry(self, justify=CENTER, foreground="grey", cursor="arrow", state="disabled", textvariable=self.value_output)
        self.ent_output.pack(fill=X)
        # event entry 'output'
        self.ent_output.bind("<Button-1>", self.selectOutput)
        # label -> position
        self.lbl_position = Label(self, text="Position", anchor=W, bg=self.cget("bg"))
        self.lbl_position.pack(fill=X, pady=(10,0))
        # combobox -> position
        self.value_positions = ["left top", "left center", "left bottom", "top", "center", "bottom", "right top", "right center", "right bottom"]
        self.cbx_position = ttk.Combobox(self, value=self.value_positions, state="readonly", justify=CENTER)
        self.cbx_position.pack(fill=X)
        # button start
        self.btn_start = ttk.Button(text="set watermark", takefocus=False, command=self.setWatermark)
        self.btn_start.pack(fill=BOTH, expand=True, pady=15)

    def callback_number(self, value):
        if str.isdigit(value) and int(value) <= 1920 and re.match("^[1-9]", value):
            self.lbl_alert.pack_forget()
            self.frame_alert["height"] = 1
            return True
        else:
            self.lbl_alert.pack(fill=X)
            return False

    def widgetLock(self, state: Literal["readonly", "disabled"]="disabled"):
        # enable 'spinbox size icon'
        self.sp_size_icon["state"] = state if self.cbx_type.get() == "Icon" else "normal"
        # enable 'entry folder images'
        self.ent_folder_images["state"] = state
        # enable 'entry output'
        self.ent_output["state"] = state
        # enable 'scale opactiy'
        self.sc_opacity_icon["state"] = "active" if state == "readonly" else state

    def setOpacityIcon(self, event):
        # get value opacity
        value = self.value_opacity_icon.get()
        # get value type
        cbx_type_value = self.cbx_type.get()
        # get value size icon
        size = 0
        
        # combobox 'type' equal to icon
        if cbx_type_value == "Icon":
            # get size icon from 'spinbox'
            sp_size = self.value_size_icon.get()
            # edit on variable size
            size = (sp_size, sp_size)

        # combobox 'type' equal to image
        if cbx_type_value == "Image":
            # get width canvas
            cn_width = self.canvas.winfo_width()
            # get height canvas
            cn_height = self.canvas.winfo_height()
            # edit on variable size
            size = (cn_width, cn_height)

        # change text label to new value opacity
        self.lbl_opacity_icon["text"] = f"Opacity: {value}"
        # change opacity watermark
        img = Image.open(self.watermark_path).convert("RGBA").resize(size)
        alpha = img.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(value/255.0)
        img.putalpha(alpha)
        # convert to "PhotoImage" for using in canvas
        icon = ImageTk.PhotoImage(img)
        # postion x on canvas
        x = (self.canvas.winfo_width() - size[0]) // 2
        # postion y on canvas
        y = (self.canvas.winfo_height() - size[1]) // 2
        # clear canvas
        self.canvas.delete(self.watermark_id)
        # set icon in canvas and save to variable 'watermark_id'
        self.watermark_id = self.canvas.create_image(x, y, image=icon, anchor=NW)
        self.canvas.image = icon

    def setType(self, event=None):
        # get type from combobox
        type_value = self.cbx_type.get()
        # get opacity
        opacity = self.value_opacity_icon.get()
        # selected "Image"
        if type_value == "Image":
            # clear canvas
            self.canvas.delete("all")
            # unlimited 'spinbox size'
            self.sp_size_icon["from_"] = 0
            self.sp_size_icon["to"] = 1920
            self.sp_size_icon["state"] = "normal"
            # variable 'watermark' not none
            if self.watermark_id:
                # get width canvas
                cn_width = self.canvas.winfo_width()
                # get height canvas
                cn_height = self.canvas.winfo_height()
                # set image in canvas
                self.setIcon(self.watermark_path, (cn_width, cn_height), opacity)

        # selected "Icon"
        if type_value == "Icon":
            # clear canvas
            self.canvas.delete("all")
            # canvas background
            self.canvas.create_image(0,0,anchor=NW, image=self.background)
            # limited 'spinbox size'
            self.sp_size_icon["from_"] = 25
            self.sp_size_icon["to"] = 256
            self.sp_size_icon["state"] = "disabled"
            # set default value 'spinbox' size
            self.value_size_icon.set(75)
            # remove alert
            self.lbl_alert.pack_forget()
            self.frame_alert["height"] = 1
            # variable 'watermark' not none
            if self.watermark_id:
                # set image in canvas
                self.setIcon(self.watermark_path, (75, 75), opacity)

    def setIcon(self, src: str, new_size: tuple[int, int]=(75, 75), opacity: int=250):
        # clear canvas
        if self.watermark_id:
            self.canvas.delete(self.watermark_id)
        # change size icon to '75x75'
        icon_resize = Image.open(src).convert("RGBA").resize(new_size, Image.LANCZOS)
        # set opacity
        alpha = icon_resize.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity/255.0)
        icon_resize.putalpha(alpha)
        # convert to "PhotoImage" for using in canvas
        icon = ImageTk.PhotoImage(icon_resize)
        # postion x on canvas
        x = (self.canvas.winfo_width() - new_size[0]) // 2
        # postion y on canvas
        y = (self.canvas.winfo_height() - new_size[1]) // 2
        # set icon in canvas and save to variable 'watermark_id'
        self.watermark_id = self.canvas.create_image(x, y, image=icon, anchor=NW)
        self.canvas.image = icon
        # save path to variable 'watermark_id'
        self.watermark_path = src
        # enable widgets
        self.widgetLock("readonly")
            
    def selectIcon(self, event=None):
        # ask open filename
        file = filedialog.askopenfilename(title="watermark | select icon", 
                                          filetypes=[("JPG", "*.jpg"), ("PNG", "*.png")])
        # variable "file" is not none
        if file:
            # get value combobox 'type'
            cbx_type_value = self.cbx_type.get()
            # combobox 'type' -> icon
            if cbx_type_value == "Icon":
                # get size icon
                size = self.value_size_icon.get()
                # handel icon
                self.setIcon(file, (size,size))
            else:
                # get width canvas
                cn_width = self.canvas.winfo_width()
                # get height canvas
                cn_height = self.canvas.winfo_height()
                # set image in canvas
                self.setIcon(file, (cn_width, cn_height))
                
            # change variable 'mode' from false to true
            self.lock_mode = True

    def resizeIcon(self):
        # get new size
        new_size = self.value_size_icon.get()
        # 'type' is not equal to Image
        if self.cbx_type.get() != "Image":
            # change size
            self.setIcon(self.watermark_path, (new_size,new_size))

    def selectFolderImages(self, event=None):
        # entry not disabled
        if self.lock_mode:
            # path folder
            folder = filedialog.askdirectory(title="watermark | select folder images")
            # check folder is not empty
            if folder:
                # change '/' to '\'
                folder = folder.replace("/", '\\')
                # set in entry 'folder images'
                self.value_folder_images.set(folder)
    
    def selectOutput(self, event=None):
        # entry not disabled
        if self.lock_mode:
            # path folder
            output = filedialog.askdirectory(title="watermark | select folder images")
            # check folder is not empty
            if output:
                # change '/' to '\'
                output = output.replace("/", '\\')
                # set in entry 'output'
                self.value_output.set(output)
                # change color text
                self.ent_output["foreground"] = "#000"

    def getPosition(self, image_size):
        # image size
        img_width = image_size[0]
        img_height = image_size[1]
        # size watermark
        size = self.value_size_icon.get()
        # x / y
        x = y = 0
        # value combobox position
        position = self.cbx_position.get()
        # check combobx position
        match position:
            case "left top":
                x = y = 0
            case "left center":
                x, y = 0, (img_height - size ) // 2
            case "left bottom":
                x, y = 0, img_height - size
            case "top":
                x, y = (img_width - size) // 2, 0
            case "center":
                x, y = (img_width - size) // 2, (img_height - size) // 2
            case "bottom":
                x, y = (img_width - size) // 2, img_height - size
            case "right top":
                x, y = img_width - size, 0
            case "right center":
                x, y = img_width - size, (img_height - size) // 2
            case "right bottom":
                x, y = img_width - size, img_height  - size
        
        # callback x,y
        return x, y

    def setWatermark(self):
        # get position
        value_position = self.cbx_position.get()
        # get folder path
        folder_images = self.value_folder_images.get()
        # get output path
        output_path = os.path.join(self.value_output.get(), value_position)
        # get size icon
        watermark_size = self.value_size_icon.get()
        # get opacity icon
        opacity = self.value_opacity_icon.get()
        # check values
        if not folder_images:
            # alert error
            messagebox.showerror("Empty", "Field \"Folder Path\" is empty")
        else:
            # show all files in folder target
            get_images = os.listdir(folder_images)
            # handel images -> 'folder images'
            image_target_list = [ os.path.join(folder_images, image) for image in get_images ]
            # handel images -> 'folder output'
            image_output_list = [ os.path.join(output_path, image) for image in get_images ]
            # watermark
            watermark = Image.open(self.watermark_path)
            # resize watermark
            watermark = watermark.resize((watermark_size, watermark_size)).convert("RGBA")
            # set opacity
            alpha = watermark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity/255.0)
            watermark.putalpha(alpha)
            # check / create folder output
            os.makedirs(output_path, exist_ok=True)
            # set watermark
            for index, image in enumerate(image_target_list):
                # get filename and file extension
                _, ext = os.path.splitext(image)
                if ext in (".jpg", ".png"):
                    # open image
                    img = Image.open(image)
                    # get size image
                    img_size = img.size
                    # get position
                    position = self.getPosition(img_size)
                    # paste watermark
                    img.paste(watermark, position, watermark)
                    # save image
                    img.save(image_output_list[index])
            
            # message complete
            messagebox.showinfo("watermark", "done")

if __name__ == "__main__":
    root = Application()
    root.mainloop()