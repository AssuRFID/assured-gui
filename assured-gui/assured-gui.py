#!/usr/bin/python
from gi.repository import Gtk, GLib, GObject
import threading, os, subprocess, atexit, sys
import requests

import restclient, addtag

class AssuredWindow(Gtk.Window):
    def __init__(self, assured_url):
        self.client = restclient.RestClient(url)
        Gtk.Window.__init__(self, title="Assured GUI")

        self.set_size_request(600, 800)
        button = Gtk.Button(label="Quit")
        button.connect("clicked", Gtk.main_quit)

        button_box = Gtk.HButtonBox()
        button_box.set_layout(Gtk.ButtonBoxStyle.END)
        button_box.add(button)
        
        self.uid_label = Gtk.Label("")

        nfc_page = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        nfc_page.set_border_width(10)
        nfc_page.add(self.uid_label)

        self.store = Gtk.ListStore(int, str, str, bool, bool)
        self.tags_view = Gtk.TreeView(self.store)
        
        name_rend = Gtk.CellRendererText()
        name_rend.connect('edited', self.name_edited)
        name_rend.set_property('editable', True)
        access_rend = Gtk.CellRendererToggle()
        access_rend.connect('toggled', self.access_toggled)
        access_rend.set_property('activatable', True)
        columns = [Gtk.TreeViewColumn("ID", Gtk.CellRendererText(), text=0),
                   Gtk.TreeViewColumn("Name", name_rend, text=1),
                   Gtk.TreeViewColumn("UID", Gtk.CellRendererText(), text=2),
                   Gtk.TreeViewColumn("Allowed in?", access_rend, active=3),
                   Gtk.TreeViewColumn("Inside?", Gtk.CellRendererToggle(), active=4)]
        for column in columns:
            self.tags_view.append_column(column)
        select = self.tags_view.get_selection()
        select.connect("changed", self.on_selection_change)

        refresh = Gtk.Button.new_with_label("Refresh")
        refresh.connect("clicked", self.refresh_tags)
        self.add_btn = Gtk.Button.new_with_label("Add tag")
        self.add_btn.set_sensitive(False)
        self.add_btn.connect("clicked", self.add_tag)
        
        self.delete_btn = Gtk.Button.new_with_label("Delete tag")
        self.delete_btn.set_sensitive(False)
        self.delete_btn.connect("clicked", self.delete_tag)
        delete_style = self.delete_btn.get_style_context()
        delete_style.add_class('destructive-action')
        
        server_btnbox = Gtk.HButtonBox()
        server_btnbox.set_layout(Gtk.ButtonBoxStyle.CENTER)
        server_btnbox.add(refresh)
        server_btnbox.add(self.delete_btn)
        server_btnbox.add(self.add_btn)
        
        server_page = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        server_page.set_border_width(10)
        server_page.add(self.tags_view)
        server_page.add(server_btnbox)

        admin_nb = Gtk.Notebook()
        admin_nb.append_page(nfc_page, Gtk.Label('RFID'))
        admin_nb.append_page(server_page, Gtk.Label('Server Database'))
        
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.set_homogeneous(False)
        vbox.pack_start(admin_nb, True, True, 0)
        vbox.pack_start(button_box, False, False, 0)
        self.add(vbox)

        nfc_worker = threading.Thread(target=self.poll)
        nfc_worker.daemon = True
        nfc_worker.start()

        self.refresh_tags()
        atexit.register(self.cleanup)
        
    def poll(self):
        path = os.path.dirname(os.path.realpath(__file__))
        cmd = os.path.join(path, "assured-nfc")
        self.nfcp = subprocess.Popen([cmd],
                                     stdout=subprocess.PIPE)
        for line in iter(self.nfcp.stdout.readline, b''):
            GLib.idle_add(self.update_uid, line.rstrip())

    # Called when a new tag is scanned
    def update_uid(self, uid):
        self.uid_label.set_text(uid)
        self.add_btn.set_sensitive(True)
        try:
            resp = self.client.auth_tag(uid)
            self
        except requests.exceptions.ConnectionError as e:
            self.error_dlg("Error connecting to server", str(e))
        except restclient.ApiError:
            self.error_dlg("User not found in database")
        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                       Gtk.ButtonsType.OK,
                                       "Welcome, " + resp['name'])
            if resp['access_room1']:
                movement = 'out of' if resp['inside_room1'] else 'into'
                dialog.format_secondary_text("You have been allowed " + movement + " Room 1.")
                self.client.tag_move(uid)
            else:
                dialog.format_secondary_text("You may not enter Room 1.")
            dialog.run()
            dialog.destroy()
            self.refresh_tags()

    def refresh_tags(self, button=None):
        try:
            tags = self.client.tags_list()
        except requests.exceptions.ConnectionError:
            self.error_dlg("Failed to connect to server")
        else:
            self.store.clear()
            for tag in tags:
                self.store.append([tag['id'],
                                   tag['name'],
                                   tag['uid'],
                                   tag['access_room1'],
                                   tag['inside_room1']])

    def add_tag(self, button):
        dialog = addtag.AddTagDialog(self, self.uid_label.get_text())
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            try:
                self.client.new_tag(dialog.name_entry.get_text(),
                                    self.uid_label.get_text(),
                                    dialog.access_room1.get_active())
            except restclient.ApiError:
                self.error_dlg("Bad request")
            self.refresh_tags()
            
        dialog.destroy()

    def delete_tag(self, button):
        selection = self.tags_view.get_selection()
        model, tagiter = selection.get_selected()
        if tagiter != None:
            try:
                self.client.del_tag(model[tagiter][0])
            except restclient.ApiError:
                self.error_dlg("Bad request")
            self.refresh_tags()

    def on_selection_change(self, selection):
        model, sel_iter = selection.get_selected()
        if sel_iter is None:
            self.delete_btn.set_sensitive(False)
        else:
            self.delete_btn.set_sensitive(True)

    def name_edited(self, rend, row, new_text):
        listiter = self.store.get_iter(row)
        self.client.update_tag(self.store[listiter][0], name=new_text)
        self.refresh_tags()

    def access_toggled(self, rend, row):
        listiter = self.store.get_iter(row)
        self.client.update_tag(self.store[listiter][0], access_room1=(not self.store[listiter][3]))
        self.refresh_tags()
            
    def error_dlg(self, error, secondary_text=None):
        error_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
                                         Gtk.ButtonsType.OK,
                                         error)
        if secondary_text is not None:
            dialog.format_secondary_text(secondary_text)
        error_dialog.run()
        error_dialog.destroy()
    
    def cleanup(self):
        self.nfcp.terminate()

if len(sys.argv) >= 2:
    url = sys.argv[1]
else:
    url = 'http://localhost/assured/api/v1.0/'
            
win = AssuredWindow(url)
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
