import re, sys, os, ftplib, threading

import pygame_sdl2
pygame_sdl2.import_as_pygame()

import pygame
from pygame.locals import *

from pgu.pgu import gui

class FTP_PDF_Upload(object):
    def __init__(self):
        pass

    def open_file_browser(self):
        file_dialog = gui.FileDialog()
        file_dialog.connect(gui.CHANGE, self.handle_file_browser_closed, file_dialog)
        file_dialog.open()

    def handle_file_browser_closed(self, file_path):
        if file_path.value:
            fp = file_path.value

        if self.is_pdf_file(fp):
            self.file_size = os.path.getsize(fp)
            self.upload_pdf(fp)
        else:
            self.not_pdf_error()

    def is_pdf_file(self, file_path):
        is_pdf = re.compile('^.*(\\.(pdf|PDF))$')

        if is_pdf.match(file_path) is not None:
            return True

        return False
    
    def not_pdf_error(self):
        self.ui = gui.Table()
        self.ui.tr()
        self.ui.td(self.error_label)
        self.ui.tr()
        self.ui.td(self.open_button)
        self.app.init(widget = self.ui, screen = self.screen)

    def upload_pdf(self, file_path):
        self.file_path = file_path
        
        self.upui = gui.Table()
        self.upui.tr()
        self.pwd_label = gui.Label('Enter password here:')
        self.upui.td(self.pwd_label)
        self.upui.tr()
        self.pwd = gui.Password(size = 16)
        #self.pwd.pcls = 'focus'
        self.pwd.focus()
        self.upui.td(self.pwd)
        self.upui.tr()
        self.file_path_label = gui.Label(file_path)
        self.upui.td(self.file_path_label)
        self.upui.tr()
        self.submit_button = gui.Button('Upload Now!')
        self.submit_button.connect(gui.CLICK, self.ftp_upload)
        self.upui.td(self.submit_button)
        self.upui.tr()
        self.back_button = gui.Button('< Back')
        self.back_button.connect(gui.CLICK, self.initial_ui)
        self.back_button.style.margin_top = 48
        self.upui.td(self.back_button)
        
        self.app.init(widget = self.upui, screen = self.screen)
        
    def ftp_upload(self):
        self.estring = None
        
        login_thread = threading.Thread(target = self.try_login)
        login_thread.daemon = True
        login_thread.start()
        login_thread.join()

        if self.estring == '530':
            self.pwd_label.set_text('Wrong Password. Please try again.')
            self.pwd_label.style.color = 'red'
        elif self.estring != None:
            self.pwd_label.set_text('Network or unknown error. Please try again.')
            self.pwd_label.style.color = 'red'
        else:
            self.prui = gui.Table()
            self.prui.tr()
            self.progress_label = gui.Label('Upload Progress')
            self.prui.td(self.progress_label)
            self.prui.tr()
            self.up_progress = gui.ProgressBar(0, 0, 100, width = 400)
            self.prui.td(self.up_progress)
            self.exit_button = gui.Button('Quit Application')
            self.exit_button.connect(gui.CLICK, lambda: sys.exit())

            self.app.init(widget = self.prui, screen = self.screen)
            
            the_upload_thread = threading.Thread(target = self.upload_thread, args = (self.ftp,))
            the_upload_thread.daemon = True
            the_upload_thread.start()
            
    def try_login(self):
        try:
            self.ftp = ftplib.FTP('ftp.ellendaleag.org', 'ellendaleag', self.pwd.value)
        except ftplib.all_errors as e:
            self.estring = str(e).split(None, 1)[0]
            
    def upload_thread(self, ftp):
        self.up_progress_value_ct = 0
        
        try:
            ftp.cwd('ellendaleag.org/user/bulletin')

            ftp.storbinary('STOR ' + 'bulletin.pdf', open(self.file_path, 'rb'), blocksize = 1024, callback = self.upload_progress_logic)
            ftp.close()

            self.doneui = gui.Table()
            self.doneui.tr()
            self.done_label = gui.Label('Upload successful! You may now close the application.')
            self.doneui.td(self.done_label)
            self.doneui.tr()
            self.doneui.td(self.exit_button)

            self.app.init(widget = self.doneui, screen = self.screen)

        except:
            self.progress_label.set_text('Upload network error. Please restart the application and try again.')
            self.progress_label.style.color = 'red'
            self.prui.tr()
            self.prui.td(self.exit_button)
                
    def upload_progress_logic(self, block):
        self.up_progress_value_ct += 100 / (self.file_size / 1024)
        self.up_progress.value = round(self.up_progress_value_ct)
        
    def initial_ui(self):
        self.ui = gui.Table()
        self.ui.tr()
        
        self.error_label = gui.Label('Invalid file type. Please choose a pdf file to upload.')
        self.error_label.style.color = 'red'
        self.error_label.style.margin_bottom = 6
        
        self.open_button = gui.Button('Choose bulletin.pdf File to Upload')
        self.open_button.connect(gui.CLICK, self.open_file_browser)

        self.ui.td(self.open_button)

        self.app.init(widget = self.ui, screen = self.screen)

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption('Website Bulletin Uploader')

        self.app = gui.Desktop(theme = gui.Theme('clean'))
            
        self.app.connect(gui.QUIT, self.app.quit, None)

        self.initial_ui()

        self.app.run()
    
if __name__ == '__main__':    
    ftp_pdf_uploader = FTP_PDF_Upload()
    ftp_pdf_uploader.run()