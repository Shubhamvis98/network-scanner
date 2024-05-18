#!/usr/bin/python3
# Author Shubham Vishwakarma
# git/twitter: ShubhamVis98

import gi, threading, subprocess, psutil
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

class AppDetails:
    appname = 'Port Scanner'
    app_info = r'''_______________________________________________
Port Scanner - An Nmap Front-End
by @ShubhamVis98
|
git/twitter: ShubhamVis98
Web: https://fossfrog.in
Youtube: fossfrog
_______________________________________________'''

class Functions:
    def get_output(self, cmd, shell=False, wait=True):
        if shell:
            run = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        else:
            run = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output = str(run.communicate()[0].decode()) if wait else ''
        returncode = run.poll()
        return [output, returncode, run]

    def terminate_processes(self, proc_name, params):
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == proc_name and params in str(proc.info['cmdline']):
                try:
                    p = psutil.Process(proc.info['pid'])
                    p.terminate()
                except psutil.NoSuchProcess as e:
                    print(f"Error terminating process {proc.info['pid']}: {e}")

    def set_app_theme(theme_name, isdark=False):
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-theme-name", theme_name)
        settings.set_property("gtk-application-prefer-dark-theme", isdark)

class SplashScreen(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=AppDetails.appname)
        self.set_default_size(600, 400)
        self.set_position(Gtk.WindowPosition.CENTER)

        image = Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file('logo.png')
        image.set_from_pixbuf(pixbuf)
        Functions.set_app_theme("Adwaita", True)

        self.add(image)
        self.show_all()

        GLib.timeout_add_seconds(2, self.close_splash_screen)

    def close_splash_screen(self):
        main_window = PSGUI().run(None)
        self.destroy()

class AboutScreen(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="About Port Scanner")
        self.set_default_size(300, 250)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)

        # Adding the logo
        logo = Gtk.Image.new_from_file("logo.png")
        logo.set_margin_top(10)  # Set top margin
        logo.set_margin_bottom(10)  # Set bottom margin
        logo.set_margin_start(10)  # Set start (left for LTR languages) margin
        logo.set_margin_end(10)  # Set end (right for LTR languages) margin
        # Set a fixed size for the image (optional)
        logo.set_size_request(100, 100)  # Set width and height
        self.box.pack_start(logo, False, False, 0)

        label_package = Gtk.Label()
        label_package.set_markup("<b>Package Name:</b> Port Scanner")
        self.box.pack_start(label_package, False, False, 0)

        label_version = Gtk.Label()
        label_version.set_markup("<b>Version:</b> 1.2")
        self.box.pack_start(label_version, False, False, 0)

        label_name = Gtk.Label()
        label_name.set_markup("<b>Developer:</b> Shubham Vishwakarma")
        self.box.pack_start(label_name, False, False, 0)

        label_website = Gtk.Label()
        label_website.set_markup("<b>Website:</b> <a href='https://fossfrog.in'>https://fossfrog.in</a>")
        label_website.set_line_wrap(True)
        label_website.connect("activate-link", self.open_website)
        self.box.pack_start(label_website, False, False, 0)

        self.close_button = Gtk.Button(label="Close")
        self.close_button.connect("clicked", self.on_close_clicked)
        self.box.pack_end(self.close_button, False, False, 0)
        self.show_all()

    def open_website(self, widget, uri):
        import webbrowser
        webbrowser.open(uri)

    def on_close_clicked(self, widget):
        self.destroy()

class Home(Functions):
    def __init__(self, builder):
        self.builder = builder
        self.target = self.builder.get_object('target')
        self.profile = self.builder.get_object('profile')
        self.opts = self.builder.get_object('opts')
        self.scan_btn = self.builder.get_object('scan_btn')
        self.status = self.builder.get_object('status')
        self.status.set_editable(False)
        self.status.set_justification(Gtk.Justification.CENTER)
        self.mi_save = self.builder.get_object('mi_save').connect("activate", self.savebuffer)
        self.mi_quit = self.builder.get_object('mi_quit').connect("activate", Gtk.main_quit)
        self.mi_about = self.builder.get_object('mi_about').connect("activate", self.about)

        self.scan_btn.set_label('Scan')
        self.target.set_placeholder_text('Target')
        # Functions.set_app_theme("Adwaita", True)

        self.profiles = [
            ('qs', 'Quick Scan'),
            ('qsp', 'Quick Scan Plus'),
            ('qt', 'Quick Traceroute'),
            ('rs', 'Regular Scan'),
            ('ps', 'Ping Scan'),
            ('is', 'Intense Scan'),
            ('isu', 'Intense Scan Plus UDP'),
            ('ist', 'Intense Scan, All TCP Ports'),
            ('isnp', 'Intense Scan, No Ping'),
            ('scs', 'Slow Comprehensive Scan'),
            ]
        self.prof_opts = {
            'qs': '-T4 -F',
            'qsp': '-sV -T4 -O -F --version-light',
            'qt': '-sn --traceroute',
            'rs': '',
            'ps': '-sn',
            'is': '-T4 -A -v',
            'isu': '-sS -sU -T4 -A -v',
            'ist': '-p 1-65535 -T4 -A -v',
            'isnp': '-T4 -A -v -Pn',
            'scs': '-sS -sU -T4 -A -v -PE -PP -PS80,443 -PA3389 -PU40125 -PY -g 53 --script "default or (discovery and safe)"',
            }

        for profile in self.profiles:
            self.profile.append(profile[0], profile[1])

        self.profile.connect('changed', self.on_profile_changed)
        self.profile.set_active(0)
        self.scan_btn.connect('clicked', self.on_scan_clicked)
        self.status_buffer = self.status.get_buffer()
        # self.status_buffer.set_text(AppDetails.app_info)

    def run(self):
        pass

    def savebuffer(self, widget):
        tmpstatus = self.getStatus()

        filechooser = Gtk.FileChooserDialog(title="Open Ducky", parent=None, action=Gtk.FileChooserAction.SAVE)
        filechooser.add_buttons("_Save", Gtk.ResponseType.OK)
        filechooser.add_buttons("_Cancel", Gtk.ResponseType.CANCEL)
        filechooser.set_default_response(Gtk.ResponseType.OK)
        response = filechooser.run()

        if response == Gtk.ResponseType.OK:
            try:
                with open(filechooser.get_filename(), 'w') as f:
                    f.write(tmpstatus)
                self.setStatus('\n\n' + 'File Saved')
            except PermissionError:
                self.setStatus('\n\n' + 'File Not Saved, !!!Access Denied!!!')
        filechooser.destroy()

    def about(self, widget):
        # self.status_buffer.set_text(AppDetails.app_info)
        AboutScreen()


    def on_profile_changed(self, widget):
        active_id = self.profile.get_active_id()
        self.opts.set_text(self.prof_opts[active_id])

    def setStatus(self, stsTxt, clear=False):
        if clear:
            tmp = stsTxt
        else:
            tmp = self.getStatus() + '\n' + stsTxt
        self.status_buffer.set_text(tmp)
    
    def getStatus(self):
        startIter, endIter = self.status_buffer.get_bounds()
        return(self.status_buffer.get_text(startIter, endIter, False))

    def on_scan_clicked(self, btn):
        self.status.set_justification(Gtk.Justification.LEFT)
        status = self.status_buffer

        target = self.target.get_text()
        opts = self.opts.get_text()

        if target == '':
            status.set_text('[!] Target is empty.')
            return

        if self.scan_btn.get_label() == 'Scan':
            status.set_text('Scanning...')
            tmp = threading.Thread(target=lambda: self.scan(target, opts)).start()
            self.scan_btn.set_label('Stop')
        else:
            self.terminate_processes('nmap', target)
            self.scan_btn.set_label('Scan')

    def scan(self, target, opts):
        status = self.status_buffer
        self.run = self.get_output(f'nmap {opts} {target}', wait=True)
        status.set_text('Scanning...')
        status.set_text(self.run[0])
        self.scan_btn.set_label('Scan')

class PSGUI(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id="in.fossfrog.portscanner")

    def do_activate(self):
        builder = Gtk.Builder()
        builder.add_from_file('portscanner.ui')

        # Initialize Functions
        Home(builder).run()

        # Get The main window from the glade file
        window = builder.get_object('ps_main')
        window.set_title(AppDetails.appname)
        window.set_default_size(600, 400)

        # Show the window
        window.connect('destroy', Gtk.main_quit)
        window.show_all()

if __name__ == "__main__":
    # nh = PSGUI().run(None)
    # Gtk.main()
    splash_screen = SplashScreen()
    Gtk.main()