#!/usr/bin/env python3
# Author: Shubham Vishwakarma
# git/twitter: ShubhamVis98

import gi, threading, subprocess, psutil
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

class AppDetails:
    appname = 'Network Scanner'
    appversion = '1.0'
    appinstallpath = '/usr/lib/networkscanner'
    ui = f'{appinstallpath}/networkscanner.ui'
    applogo = f'{appinstallpath}/logo.svg'
    app_info = f'''_______________________________________________
{appname} {appversion} - An Nmap Front-End
by @ShubhamVis98

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
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(AppDetails.applogo)
        scaled_pixbuf = pixbuf.scale_simple(200, 200, GdkPixbuf.InterpType.BILINEAR)
        image.set_from_pixbuf(scaled_pixbuf)
        Functions.set_app_theme("Adwaita", True)

        self.add(image)
        self.show_all()

        GLib.timeout_add_seconds(2, self.close_splash_screen)

    def close_splash_screen(self):
        main_window = NSGUI().run(None)
        self.destroy()

class AboutScreen(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="About")
        # self.set_default_size(300, 250)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)

        # Adding the logo
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(AppDetails.applogo)
        scaled_pixbuf = pixbuf.scale_simple(200, 200, GdkPixbuf.InterpType.BILINEAR)
        logo = Gtk.Image.new_from_pixbuf(scaled_pixbuf)
        self.box.pack_start(logo, False, False, 10)

        label_package = Gtk.Label()
        label_package.set_markup(f'<b>{AppDetails.appname} {AppDetails.appversion}</b>')
        self.box.pack_start(label_package, False, False, 0)
        
        label_desc = Gtk.Label()
        label_desc.set_markup("An Nmap Front-end for GNU/Linux Phones")
        label_desc.set_margin_start(20)
        label_desc.set_margin_end(20)
        self.box.pack_start(label_desc, False, False, 0)

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
        return True

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

        self.profiles = {
            'Quick Scan': '-T4 -F',
            'Quick Scan Plus': '-sV -T4 -O -F --version-light',
            'Quick Traceroute': '-sn --traceroute',
            'Regular Scan': '',
            'Ping Scan': '-sn',
            'Intense Scan': '-T4 -A -v',
            'Intense Scan Plus UDP': '-sS -sU -T4 -A -v',
            'Intense Scan, All TCP Ports': '-p 1-65535 -T4 -A -v',
            'Intense Scan, No Ping': '-T4 -A -v -Pn',
            'Slow Comprehensive Scan': '-sS -sU -T4 -A -v -PE -PP -PS80,443 -PA3389 -PU40125 -PY -g 53 --script "default or (discovery and safe)"',
            'Scan Vulnerabilities (vuln)': '--script vuln',
            'Scan Vulnerabilities (vulners)': '-sV --script vulners',
        }

        for profile in self.profiles.keys():
            self.profile.append_text(profile)

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
        self.opts.set_text(self.profiles[self.profile.get_active_text()])

    def setStatus(self, stsTxt=False, clear=False):
        if clear:
            self.status_buffer.delete(self.status_buffer.get_start_iter(), self.status_buffer.get_end_iter())
        if stsTxt:
            self.status_buffer.insert(self.status_buffer.get_end_iter(), stsTxt)
        GLib.idle_add(self.scroll_to_end, self.status_buffer)

    def getStatus(self):
        startIter, endIter = self.status_buffer.get_bounds()
        return(self.status_buffer.get_text(startIter, endIter, False))

    def scroll_to_end(self, buffer):
        end_iter = buffer.get_end_iter()
        self.status.scroll_to_iter(end_iter, 0.0, True, 0.0, 1.0)

    def on_scan_clicked(self, btn):
        self.status.set_justification(Gtk.Justification.LEFT)
        target = self.target.get_text()
        opts = self.opts.get_text()

        if target == '':
            self.setStatus('[!] Target is empty.', True)
            return

        if self.scan_btn.get_label() == 'Scan':
            self.setStatus(False, True)
            self.process = subprocess.Popen(f'nmap {opts} {target}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            threading.Thread(target=self.read_output).start()
            self.scan_btn.set_label('Stop')
        else:
            # self.terminate_processes('nmap', target)
            self.process.terminate()
            self.process = None
            self.setStatus('\n\nTerminated')
            self.scan_btn.set_label('Scan')

    def read_output(self):
        try:
            while self.process.poll() is None:
                line = self.process.stdout.readline().decode('utf-8')
                if line:
                    GLib.idle_add(self.setStatus, line)
        except AttributeError:
            pass
        self.scan_btn.set_label('Scan')

class NSGUI(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id="in.fossfrog.networkscanner")

    def do_activate(self):
        builder = Gtk.Builder()
        builder.add_from_file(AppDetails.ui)

        # Initialize Functions
        Home(builder).run()

        # Get The main window from the glade file
        window = builder.get_object('ns_main')
        window.set_title(AppDetails.appname)
        window.set_default_size(600, 400)

        # Show the window
        window.connect('destroy', Gtk.main_quit)
        window.show_all()

if __name__ == "__main__":
    # nh = NSGUI().run(None)
    # Gtk.main()
    splash_screen = SplashScreen()
    Gtk.main()
