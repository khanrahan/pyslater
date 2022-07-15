"""
https://github.com/khanrahan/pyslater
"""


from __future__ import print_function
from functools import partial
from PySide2 import QtCore
from PySide2 import QtWidgets
import os


CMD_NAME = "pyslater.py"
DEFAULT_TEMPLATE = "templates/default_template_16x9.ttg"
DEFAULT_OUTPUT_TTG = "<Spot Code>_<Duration>_<Title>.ttg"
GSHEET = "https://docs.google.com/spreadsheets/d/1msDmKt5sigbVe1Pmjsinw2pUqw03hi6Tdo8C0yYehzA/edit?usp=sharing"
SETUPS_ROOT = "/opt/Autodesk/project"


class FlameButton(QtWidgets.QPushButton):                                      
    """                                                                        
    Custom Qt Flame Button Widget                                              
    To use:                                                                    
    button = FlameButton('Button Name', do_when_pressed, window)               
    """                                                                        
                                                                               
    def __init__(self, button_name, do_when_pressed, parent_window, *args, **kwargs):
        super(FlameButton, self).__init__(*args, **kwargs)                     
                                                                               
        self.setText(button_name)                                              
        self.setParent(parent_window)                                          
        self.setMinimumSize(QtCore.QSize(110, 28))                             
        self.setMaximumSize(QtCore.QSize(110, 28))                             
        self.setFocusPolicy(QtCore.Qt.NoFocus)                                 
        self.clicked.connect(do_when_pressed)                                  
        self.setStyleSheet("""QPushButton {color: #9a9a9a;                     
                                           background-color: #424142;          
                                           border-top: 1px inset #555555;      
                                           border-bottom: 1px inset black;     
                                           font: 14px 'Discreet'}              
                           QPushButton:pressed {color: #d9d9d9;                
                                                background-color: #4f4f4f;     
                                                border-top: 1px inset #666666; 
                                                font: italic}                  
                           QPushButton:disabled {color: #747474;               
                                                 background-color: #353535;    
                                                 border-top: 1px solid #444444;
                                                 border-bottom: 1px solid #242424}
                           QToolTip {color: black;                             
                                     background-color: #ffffde;                
                                     border: black solid 1px}""")

class FlameGroupBox(QtWidgets.QGroupBox):
    """ """
    
    def __init__(self, group_name, parent_window, *args, **kwargs):
        super (FlameGroupBox, self).__init__(*args, **kwargs)

        self.setTitle(group_name)
        self.setParent(parent_window)


class FlameLabel(QtWidgets.QLabel):                                            
    """                                                                        
    Custom Qt Flame Label Widget                                               
    For different label looks set label_type as: 'normal', 'background', or 'outline'
    To use:                                                                    
    label = FlameLabel('Label Name', 'normal', window)                         
    """                                                                        
                                                                               
    def __init__(self, label_name, label_type, parent_window, *args, **kwargs):
        super(FlameLabel, self).__init__(*args, **kwargs)                      
                                                                               
        self.setText(label_name)                                               
        self.setParent(parent_window)                                          
        self.setMinimumSize(110, 28)                                           
        self.setMaximumHeight(28)                                              
        self.setFocusPolicy(QtCore.Qt.NoFocus)                                 
                                                                               
        # Set label stylesheet based on label_type                             
                                                                               
        if label_type == 'normal':                                             
            self.setStyleSheet("""QLabel {color: #9a9a9a;                      
                                          border-bottom: 1px inset #282828;    
                                          font: 14px 'Discreet'}               
                                  QLabel:disabled {color: #6a6a6a}""")         
        elif label_type == 'background':                                       
            self.setAlignment(QtCore.Qt.AlignCenter)                           
            self.setStyleSheet("""QLabel {color: #9a9a9a;                      
                                          background-color: #393939;           
                                          font: 14px 'Discreet'}               
                                  QLabel:disabled {color: #6a6a6a}""")         
        elif label_type == 'outline':                                          
            self.setAlignment(QtCore.Qt.AlignCenter)                           
            self.setStyleSheet("""QLabel {color: #9a9a9a;                      
                                          background-color: #212121;           
                                          border: 1px solid #404040;           
                                          font: 14px 'Discreet'}               
                                  QLabel:disabled {color: #6a6a6a}""")


class FlameLineEdit(QtWidgets.QLineEdit):                                      
    """                                                                        
    Custom Qt Flame Line Edit Widget                                           
    Main window should include this: window.setFocusPolicy(QtCore.Qt.StrongFocus)
    To use:                                                                    
    line_edit = FlameLineEdit('Some text here', "line_edit_style", window)                        
    """                                                                        
                                                                               
    def __init__(self, text, line_edit_type, parent_window, *args, **kwargs):                  
        super(FlameLineEdit, self).__init__(*args, **kwargs)                   
                                                                               
        self.setText(text)                                                     
        self.setParent(parent_window)                                          
        self.setMinimumHeight(28)                                              
        self.setMinimumWidth(110)                                              
        # self.setFocusPolicy(QtCore.Qt.NoFocus)                               

        # Set Line Edit stylesheet based on line_edit_type
        if line_edit_type == "normal":
            self.setStyleSheet("""QLineEdit {color: #9a9a9a;                       
                                             background-color: #373e47;            
                                             selection-color: #262626;             
                                             selection-background-color: #b8b1a7;  
                                             font: 14px 'Discreet'}                
                                  QLineEdit:focus {background-color: #474e58}      
                                  QLineEdit:disabled {color: #6a6a6a;              
                                                      background-color: #373737}   
                                  QToolTip {color: black;                          
                                            background-color: #ffffde;             
                                            border: black solid 1px}
                                            """)
        elif line_edit_type == "read_only":
            self.setReadOnly(True)
            self.setStyleSheet("""QLineEdit {color: rgb(106, 106,106);
                                             background-color: rgb(28, 28, 28);    
                                             border: 1px solid rgb(55, 55, 55)} 
                                             font: 14px 'Discreet'}                
                                  QLineEdit:disabled {color: #6a6a6a;              
                                                      background-color: #373737}   
                                  QToolTip {color: black;                          
                                            background-color: #ffffde;             
                                            border: black solid 1px}
                                            """)


class FlameLineEditFileBrowse(QtWidgets.QLineEdit):                            
    """                                                                        
    Custom Qt Flame Clickable Line Edit Widget with File Browser               
    To use:                                                                    
    lineedit = FlameLineEditFileBrowse('some_path', 'Python (*.py)', window)   
    file_path: Path browser will open to. If set to root folder (/), browser will open to user home directory
    filter_type: Type of file browser will filter_type for. If set to 'dir', browser will select directory
    """                                                                        
                                                                               
    clicked = QtCore.Signal()                                                  
                                                                               
    def __init__(self, file_path, filter_type, parent, *args, **kwargs):       
        super(FlameLineEditFileBrowse, self).__init__(*args, **kwargs)         
                                                                               
        self.filter_type = filter_type                                         
        self.file_path = file_path                                             
        self.path_new = ""                                                     
                                                                               
        self.setText(file_path)                                                
        self.setParent(parent)                                                 
        self.setMinimumHeight(28)                                              
        self.setReadOnly(True)                                                 
        self.setFocusPolicy(QtCore.Qt.NoFocus)                                 
        self.clicked.connect(self.file_browse)                                 
        self.setStyleSheet("""QLineEdit {color: #898989;
                                         background-color: #373e47;
                                         font: 14px 'Discreet'}
                              QLineEdit:disabled {color: #6a6a6a;
                                                  background-color: #373737}""")
                                                                               
                                                                               
    def mousePressEvent(self, event):                                          
        if event.button() == QtCore.Qt.LeftButton:                             
            self.setStyleSheet('QLineEdit {color: #bbbbbb; background-color: #474e58; font: 14px "Discreet"}'
                               'QLineEdit:disabled {color: #6a6a6a; background-color: #373737}')
            self.clicked.emit()                                                
            self.setStyleSheet('QLineEdit {color: #898989; background-color: #373e47; font: 14px "Discreet"}'
                               'QLineEdit:disabled {color: #6a6a6a; background-color: #373737}')
        else:                                                                  
            super().mousePressEvent(event)                                     
                                                                               
                                                                               
    def file_browse(self):                                                     
        #from PySide2 import QtWidgets                                         
                                                                               
        file_browser = QtWidgets.QFileDialog()                                 
                                                                               
        # If no path go to user home directory                                 
                                                                               
        if self.file_path == '/':                                              
            self.file_path = os.path.expanduser("~")                           
        if os.path.isfile(self.file_path):                                     
            self.file_path = self.file_path.rsplit('/', 1)[0]                  
                                                                               
        file_browser.setDirectory(self.file_path)                              
                                                                               
        # If filter_type set to dir, open Directory Browser, if anything else, open File Browser
                                                                               
        if self.filter_type == 'dir':                                          
            file_browser.setFileMode(QtWidgets.QFileDialog.Directory)          
            if file_browser.exec_():                                           
                self.path_new = file_browser.selectedFiles()[0]                
                self.setText(self.path_new)                                    
        else:                                                                  
            file_browser.setFileMode(QtWidgets.QFileDialog.ExistingFile)  # Change to ExistingFiles to capture many files
            file_browser.setNameFilter(self.filter_type)                       
            if file_browser.exec_():                                           
                self.path_new = file_browser.selectedFiles()[0]                
                self.setText(self.path_new)  


class FlamePushButton(QtWidgets.QPushButton):                                  
    """                                                                        
    Custom Qt Flame Push Button Widget                                         
    """                                                                        
                                                                               
    def __init__(self, name, parent, checked, connect, *args, **kwargs):       
        super(FlamePushButton, self).__init__(*args, **kwargs)                 
                                                                               
        self.setText(name)                                                     
        self.setParent(parent)                                                 
        self.setCheckable(True)                                                
        self.setChecked(checked)                                               
        self.clicked.connect(connect)                                          
        self.setFocusPolicy(QtCore.Qt.NoFocus)                                 
        self.setMinimumSize(110, 28)                                           
        self.setMaximumSize(110, 28)                                           
        self.setStyleSheet('QPushButton {color: #9a9a9a; background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: .90 #424142, stop: .91 #2e3b48); text-align: left; border-top: 1px inset #555555; border-bottom: 1px inset black; font: 14px "Discreet"}'
                           'QPushButton:checked {color: #d9d9d9; background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: .90 #4f4f4f, stop: .91 #5a7fb4); font: italic; border: 1px inset black; border-bottom: 1px inset #404040; border-right: 1px inset #404040}'
                           'QPushButton:disabled {color: #6a6a6a; background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: .93 #383838, stop: .94 #353535); font: light; border-top: 1px solid #575757; border-bottom: 1px solid #242424; border-right: 1px solid #353535; border-left: 1px solid #353535}')


class FlamePushButtonMenu(QtWidgets.QPushButton):                              
    """                                                                        
    Custom Qt Flame Push Button Menu Widget                                    
    requires from functools import partial
    """                                                                        
                                                                               
    def __init__(self, button_name, menu_options, regen_text_fx, parent, *args, **kwargs):
        super(FlamePushButtonMenu, self).__init__(*args, **kwargs)             
                                                                               
        self.setText(button_name)                                              
        self.setParent(parent)                                                 
        self.setMinimumHeight(28)                                              
        self.setMinimumWidth(110)                                              
        self.setFocusPolicy(QtCore.Qt.NoFocus)                                 
        self.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #24303d; font: 14px "Discreet"}'
                           'QPushButton:disabled {color: #747474; background-color: #353535; border-top: 1px solid #444444; border-bottom: 1px solid #242424}')
                                                                               
        def create_menu(option):                                               
                                                                               
            self.setText(option)                                               
            justify_changed = True  # i dont think does anything.  needs to be like v2.0
            regen_text_fx(justify_changed)                                     
                                                                               
        pushbutton_menu = QtWidgets.QMenu(parent)                              
        pushbutton_menu.setFocusPolicy(QtCore.Qt.NoFocus)                      
        pushbutton_menu.setStyleSheet('QMenu {color: #9a9a9a; background-color:#24303d; font: 14px "Discreet"}'
                                      'QMenu::item:selected {color: #d9d9d9; background-color: #3a4551}')
        for option in menu_options:                                            
            pushbutton_menu.addAction(option, partial(create_menu, option))    
                                                                               
        self.setMenu(pushbutton_menu)


class PySlaterWindow(object):
    """ """

    def __init__(self, selection):  #why is selection needed?

        self.cmd_dir = self.get_cmd_dir()
        self.cmd_path = self.get_cmd_path(CMD_NAME)

        self.project_name = self.get_project_name()

        self.default_path = self.realpath_join(
                [SETUPS_ROOT, self.project_name,  "text", "flame"])

        self.csv_file_path = self.default_path

        self.filter_exclude = ""
        self.filter_include = ""

        self.ttg_file_path = self.path_join(
                [self.cmd_dir, DEFAULT_TEMPLATE])

        self.output_template_path = self.get_output_template()

        self.html = ""
        self.html_path = self.get_html_path()

        self.process = None
        self.window_size = {"x": 1000, "y": 756} 
       
        self.main_window()
        self.update_html_line_edit()


    @staticmethod                                                                       
    def copy_to_clipboard(text):                                                        
        """Self explanitory.  Only takes a string."""                                   
                                                                                        
        qt_app_instance = QtWidgets.QApplication.instance()                             
        qt_app_instance.clipboard().setText(text)


    @staticmethod
    def get_cmd_dir():
        """ """

        dirpath = os.path.realpath(os.path.dirname(__file__))

        return dirpath
     

    @staticmethod
    def get_project_name():
        """ """

        import flame

        project_name = flame.project.current_project.project_name

        return project_name


    @staticmethod
    def path_join(paths):
        """Takes a list of paths."""

        full_path = os.path.join(*paths)

        return full_path


    @staticmethod
    def realpath_join(paths):
        """ """

        path = os.path.join(*paths)
        real_path = os.path.realpath(path)

        return real_path


    def copy_csv_to_clipboard(self):
        """ """

        self.copy_to_clipboard(self.csv_path_line_edit.text())
        self.message("CSV copied to clipboard.")


    def copy_html_to_clipboard(self):
        """ """

        self.copy_to_clipboard(self.html_path_line_edit.text())
        self.message("HTML copied to clipboard.")


    def copy_url_to_clipboard(self):
        """ """

        self.copy_to_clipboard(self.url_line_edit.text())
        self.message("URL copied to clipboard.")


    def filter_exclude_btn_toggle(self):
        """ """

        if not self.filter_exclude_line_edit.isEnabled():
            self.filter_exclude_line_edit.setEnabled(True)

            self.filter_include_btn.setChecked(False)
            self.filter_include_line_edit.setEnabled(False)
        else:
            self.filter_exclude_line_edit.setEnabled(False)

        self.get_filter_exclude()


    def filter_include_btn_toggle(self):
        """ """

        if not self.filter_include_line_edit.isEnabled():
            self.filter_include_line_edit.setEnabled(True)

            self.filter_exclude_btn.setChecked(False)
            self.filter_exclude_line_edit.setEnabled(False)
        else:
            self.filter_include_line_edit.setEnabled(False)

        self.get_filter_include()


    def ttg_btn_toggle(self):
        """ """
        
        if self.ttg_path_line_edit.isEnabled():
            self.ttg_path_line_edit.setEnabled(False)
            self.ttg_file_path = ""
        else:
            self.ttg_path_line_edit.setEnabled(True)
            self.ttg_file_path = self.ttg_path_line_edit.text()

        self.get_ttg_file_path()


    def html_btn_toggle(self):
        """ """
        
        if self.html_path_line_edit.isEnabled():
            self.html_path_line_edit.setEnabled(False)
            self.html = "--no-html"
        else:
            self.html_path_line_edit.setEnabled(True)
            self.html = ""


    def get_csv_path(self):
        """ """

        self.csv_file_path = self.csv_path_line_edit.text()


    def get_filter_exclude(self):
        """ """
        
        if self.filter_exclude_line_edit.isEnabled():
            cmd_line_opt = "--exclude"
            filter_args = self.filter_exclude_line_edit.text()
            opt_and_args = [cmd_line_opt, filter_args]

            self.filter_exclude = opt_and_args
        else:
            self.filter_exclude = []


    def get_filter_include(self):
        """ """ 
        
        if self.filter_include_line_edit.isEnabled():
            cmd_line_opt = "--include"
            filter_args = self.filter_include_line_edit.text()
            opt_and_args = [cmd_line_opt, filter_args]

            self.filter_include = opt_and_args
        else:
            self.filter_include = []


    def get_cmd_path(self, cmd):
        """ """

        return os.path.join(self.cmd_dir, cmd)


    def get_html_path(self):
        """ """

        html = "copy_paster.html"
        path = os.path.join(self.default_path, html)

        return path


    def get_ttg_file_path(self):
        """Returns path to the TTG if enabled in GUI to be used an arg for the
        pyslater cmd line."""
        

        if self.ttg_path_line_edit.isEnabled():
            self.ttg_file_path = self.ttg_path_line_edit.text()
        else:
            self.ttg_file_path = ""


    def get_output_template(self):
        """ """

        path = os.path.join(self.default_path, DEFAULT_OUTPUT_TTG)

        return path


    def message(self, string):
        """ """

        self.text.appendPlainText(string)


    def update_html_line_edit(self):
        """ """

        if os.path.isfile(self.html_path):
            self.html_path_line_edit.setText(self.html_path)
        else:
            self.html_path_line_edit.setText("")

        
    def process_start(self):
        """ """

        if self.process is None:  # No process already running.
            self.message("Process starting up...")
            self.process = QtCore.QProcess()

            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.stateChanged.connect(self.handle_state)
            self.process.finished.connect(self.process_finished)

            cmd = "python"

            full_opts = []
            full_opts.append(self.cmd_path)
            #full_opts.append("-h")  # Will override other opts
            full_opts.append("--force-overwrite")
            full_opts.append(self.html)
            full_opts.extend(self.filter_exclude)
            full_opts.extend(self.filter_include)
            full_opts.extend(["-o", self.output_template_path])
            full_opts.extend([self.csv_file_path, self.ttg_file_path])

            #opts = filter(None, full_opts)  # Remove "" from the list
            opts = [opt for opt in full_opts if opt is not ""]  # Remove empty opts

            # Debug command to be run
            full_cmd = cmd + " " + " ".join(opts)
            print(full_cmd)

            self.process.start(cmd, opts)


    def process_finished(self):
        """ """

        self.message("Process all done!")
        self.process = None

        self.update_html_line_edit()  # update HTML line if HTML file now exists


    def handle_stderr(self):
        """ """

        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)


    def handle_stdout(self):
        """ """

        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)


    def handle_state(self, state):
        """ """

        states = {
            QtCore.QProcess.NotRunning: "Not running",
            QtCore.QProcess.Starting: "Starting",
            QtCore.QProcess.Running: "Running"}
        state_name = states[state]
        self.message("State changed: {}".format(state_name))


    def main_window(self):
        """ """ 
       
        def okay_button():
            """ """

            self.text.clear()  # Clear the previous shell output
            self.process_start()


        self.window = QtWidgets.QWidget()                                      

        self.window.setMinimumSize(self.window_size["x"], self.window_size["y"])                                   
        self.window.setStyleSheet('background-color: #272727')                 
        self.window.setWindowTitle("Lets Generate some Slate!")                    
                                                                               
        # FlameLineEdit class needs this                                       
        self.window.setFocusPolicy(QtCore.Qt.StrongFocus)                      
                                                                               
        # Labels                                                               
        self.input_label = FlameLabel('Input', 'background', self.window)
        self.url_label = FlameLabel('URL', 'normal', self.window)
        self.csv_label = FlameLabel('CSV File', 'normal', self.window) 

        self.filter_label = FlameLabel('Filtering', 'background', self.window)

        self.output_label = FlameLabel("Output", 'background', self.window)

        self.output_template_label = FlameLabel(
                "Output Path", 'normal', self.window)

        # Buttons                                                              
        self.ok_btn = FlameButton('Ok', okay_button, self.window)              
        self.ok_btn.setStyleSheet('background: #732020')                       
                                                                               
        self.cancel_btn = FlameButton(
                "Cancel", self.window.close, self.window)

        self.url_copy_btn = FlameButton(
                "Copy", self.copy_url_to_clipboard, self.window)

        self.csv_copy_btn = FlameButton(
                "Copy", self.copy_csv_to_clipboard, self.window)

        self.filter_exclude_btn = FlamePushButton(
                " Exclude", self.window, False, self.filter_exclude_btn_toggle)

        self.filter_include_btn = FlamePushButton(
                " Include", self.window, False, self.filter_include_btn_toggle)

        self.ttg_template_btn = FlamePushButton(
                " TTG Template", self.window, True, self.ttg_btn_toggle)

        self.html_btn = FlamePushButton(
                " HTML", self.window, True, self.html_btn_toggle)

        self.html_copy_btn = FlameButton(
                "Copy", self.copy_html_to_clipboard, self.window)
         
        # Line Edits                                                           
        self.url_line_edit = FlameLineEdit(GSHEET, "read_only", self.window)

        self.csv_path_line_edit = FlameLineEditFileBrowse(
                self.csv_file_path, "*.csv", self.window)   
        self.csv_path_line_edit.textChanged.connect(self.get_csv_path)

        self.ttg_path_line_edit = FlameLineEditFileBrowse(
                self.ttg_file_path, "*.ttg", self.window)
        self.ttg_path_line_edit.textChanged.connect(self.get_ttg_file_path)

        self.filter_include_line_edit = FlameLineEdit("", "normal", self.window)
        self.filter_include_line_edit.setEnabled(False)  # initial state
        self.filter_include_line_edit.textChanged.connect(self.get_filter_include)

        self.filter_exclude_line_edit = FlameLineEdit("", "normal", self.window)
        self.filter_exclude_line_edit.setEnabled(False)  # initial state
        self.filter_exclude_line_edit.textChanged.connect(self.get_filter_exclude)

        self.output_template = FlameLineEdit(
                self.output_template_path, "read_only", self.window)

        self.html_path_line_edit = FlameLineEdit("", "read_only", self.window)

        # Text Field
        self.text = QtWidgets.QPlainTextEdit() 
        self.text.setFont("monospace")
        self.text.setReadOnly(True)

        # Layout - Input
        self.grid1 = QtWidgets.QGridLayout()                                    
        self.grid1.setVerticalSpacing(10)                                       
        self.grid1.setHorizontalSpacing(10)                                     
        self.grid1.addWidget(self.input_label, 0, 0, 1, 3)
        self.grid1.addWidget(self.url_label, 1, 0)
        self.grid1.addWidget(self.url_line_edit, 1, 1)
        self.grid1.addWidget(self.url_copy_btn, 1, 2)
        self.grid1.addWidget(self.csv_label, 2, 0)                            
        self.grid1.addWidget(self.csv_path_line_edit, 2, 1)                             
        self.grid1.addWidget(self.csv_copy_btn, 2, 2)

        # Layout - Filtering
        self.grid2 = QtWidgets.QGridLayout()
        self.grid2.setVerticalSpacing(10)                                       
        self.grid2.setHorizontalSpacing(10)                                     
        self.grid2.addWidget(self.filter_label, 0, 0, 1, 2)
        self.grid2.addWidget(self.filter_include_btn, 1, 0)
        self.grid2.addWidget(self.filter_include_line_edit, 1, 1)
        self.grid2.addWidget(self.filter_exclude_btn, 2, 0)
        self.grid2.addWidget(self.filter_exclude_line_edit, 2, 1)

        # Layout - Output
        self.grid3 = QtWidgets.QGridLayout()
        self.grid3.setVerticalSpacing(10)                                       
        self.grid3.setHorizontalSpacing(10)
        self.grid3.addWidget(self.output_label, 0, 0, 1, 3)
        self.grid3.addWidget(self.output_template_label, 1, 0)
        self.grid3.addWidget(self.output_template, 1, 1)
        self.grid3.addWidget(self.ttg_template_btn, 2, 0)
        self.grid3.addWidget(self.ttg_path_line_edit, 2, 1)
        self.grid3.addWidget(self.html_btn, 3, 0)
        self.grid3.addWidget(self.html_path_line_edit, 3, 1)
        self.grid3.addWidget(self.html_copy_btn, 3, 2)
                                                                               
        # Layout
        self.hbox01 = QtWidgets.QHBoxLayout()                                  
        self.hbox01.addStretch(1)                                              
        self.hbox01.addWidget(self.cancel_btn)                                 
        self.hbox01.addWidget(self.ok_btn)                                     
                                                                               
        self.vbox = QtWidgets.QVBoxLayout()                                    
        self.vbox.setMargin(20)                                                
        self.vbox.addLayout(self.grid1)                                         
        self.vbox.addSpacing(40)
        self.vbox.addLayout(self.grid2)                                         
        self.vbox.addSpacing(46)
        self.vbox.addLayout(self.grid3)                                         
        self.vbox.addSpacing(26)
        self.vbox.addLayout(self.hbox01)                                       
        self.vbox.addSpacing(10)
        self.vbox.addWidget(self.text)
                                                                               
        self.window.setLayout(self.vbox)                                       
                                                                               
        # Center Window                                                        
        resolution = QtWidgets.QDesktopWidget().screenGeometry()               
         
        self.window.move(resolution.center().x() - self.window_size["x"] / 2,
                         resolution.center().y() - self.window_size["y"] / 2)

        self.window.show()                                                     
        return self.window 


def get_main_menu_custom_ui_actions():                                         
    return [{"name": "Slates...",                                               
             "actions": [{"name": "pySlater",                     
                          "execute": PySlaterWindow,                                      
                          "minimumVersion": "2020.3.1"}]                         
           }]
