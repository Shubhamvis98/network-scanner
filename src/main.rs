use std::process::{Command, Output};
use gtk4::prelude::*;
use gtk4::{Application, ApplicationWindow, Button, ComboBoxText, ScrolledWindow, TextView, TextBuffer, Box, Orientation, Entry};
use glib::clone;

fn main() {
    // Initialize GTK application
    let application = Application::builder()
        .application_id("in.fossfrog.port_scanner")
        .build();

    let app_info = "_______________________________________________
Port Scanner - An Nmap Front-End
by @ShubhamVis98
|
git/twitter: ShubhamVis98
Web: https://fossfrog.in
Youtube: fossfrog
_______________________________________________";

    // Connect activate signal
    application.connect_activate(|app| {
        // Create the main window
        let window = ApplicationWindow::builder()
            .application(app)
            .title("Port Scanner")
            .default_width(600)
            .default_height(400)
            .build();

        // Create a box to hold the elements
        let main_box = Box::builder()
            .orientation(Orientation::Vertical)
            .spacing(5)
            .build();

        // Create text input box named "target"
        let target_entry = Entry::builder()
            .placeholder_text("Target")
            .build();

        // Create a combo box named "profile"
        let profile_combo = ComboBoxText::builder().build();
        let scan_profiles = vec![
            ("Regular Scan", ""),
            ("Quick Scan", "-T4 -F"),
            ("Quick Scan Plus", "-sV -T4 -O -F --version-light"),
            ("Quick Traceroute", "-sn --traceroute"),
            ("Ping Scan", "-sn"),
            ("Intense Scan", "-T4 -A -v"),
            ("Intense Scan Plus UDP", "-sS -sU -T4 -A -v"),
            ("Intense Scan, All TCP Ports", "-p 1-65535 -T4 -A -v"),
            ("Intense Scan, No Ping", "-T4 -A -v -Pn"),
            ("Slow Comprehensive Scan", "-sS -sU -T4 -A -v -PE -PP -PS80,443 -PA3389 -PU40125 -PY -g 53 --script \"default or (discovery and safe)\""),
            ];

        for (desc, cmd) in &scan_profiles {
            profile_combo.append(Some(cmd), desc);
        }
        profile_combo.set_active(Some(0));

        // Create another text input box named "params"
        let params_entry = Entry::builder()
            .placeholder_text("Parameters")
            .build();

        profile_combo.connect_changed(clone!(@strong params_entry => move |profile_combo| {
            if let Some(text) = profile_combo.active_text() {
                if let Some(command) = find_command(&scan_profiles, &text) {
                    params_entry.set_text(command);
                }
            }
        }));

        // Create a scan button
        let scan_button = Button::with_label("Scan");

        // Create a scrolled window to hold the status text view
        let scrolled_window = ScrolledWindow::builder()
        .vexpand(true)
        .hexpand(true)
        .build();

        // Create a text view
        let status_text_view = TextView::builder().build();
        let buffer = TextBuffer::new(None);
        status_text_view.set_editable(false);
        status_text_view.set_buffer(Some(&buffer));
        buffer.set_text(app_info);

        // Add all elements to the main box
        main_box.append(&target_entry);
        main_box.append(&profile_combo);
        main_box.append(&params_entry);
        main_box.append(&scan_button);
        main_box.append(&scrolled_window);

        // Set the text view as the child of the scrolled window
        scrolled_window.set_child(Some(&status_text_view));

        // Add the main box to the window
        window.set_child(Some(&main_box));

        // Show all elements
        window.show();

        scan_button.connect_clicked(move |_| {
            let target = &target_entry.text();
            let params = &params_entry.text();
            if let Ok(output) = run_command(target, params) {
                buffer.set_text(&output);
            } else {
                buffer.set_text("Error!");
            }
        });
    });

    // Run the application
    application.run();
}

fn run_command(target: &str, params: &str) -> Result<String, std::io::Error> {
    // Execute the command
    let output: Output = Command::new("nmap")
    .arg(params)
    .arg(target)
    .output()?;
    
    // Check if the command execution was successful
    if output.status.success() {
        // Convert the output bytes to a String
        let output_string = String::from_utf8_lossy(&output.stdout).into_owned();
        Ok(output_string)
    } else {
        // If the command failed, return the error message
        let error_message = String::from_utf8_lossy(&output.stderr).into_owned();
        Err(std::io::Error::new(std::io::ErrorKind::Other, error_message))
    }
}

fn find_command<'a>(scan_profiles: &'a Vec<(&'a str, &'a str)>, description: &str) -> Option<&'a str> {
    for (desc, cmd) in scan_profiles {
        if *desc == description {
            return Some(cmd);
        }
    }
    None
}
