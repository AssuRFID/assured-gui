from gi.repository import Gtk

class AddTagDialog(Gtk.Dialog):
    def __init__(self, parent, uid):
        Gtk.Dialog.__init__(self, "Add new tag", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(150, 300)

        label = Gtk.Label("Ello")

        self.uid = "7357"
        grid = Gtk.Grid()
        grid.set_row_homogeneous(True)

        grid.add(Gtk.Label("Name", halign=Gtk.Align.END))
        self.name_entry = Gtk.Entry()
        grid.attach(self.name_entry, 1, 0, 1, 1)
        
        grid.attach(Gtk.Label("UID from scanner", halign=Gtk.Align.END), 0, 1, 1, 1)
        grid.attach(Gtk.Label(uid, halign=Gtk.Align.START), 1, 1, 1, 1)

        grid.attach(Gtk.Label("Allowed into Room 1", halign=Gtk.Align.END), 0, 2, 1, 1)
        self.access_room1 = Gtk.CheckButton()
        grid.attach(self.access_room1, 1, 2, 1, 1,)
        
        box = self.get_content_area()
        box.add(grid)
        self.show_all()
