import os
import hyperdiv as hd

class time(hd.Plugin):
    _assets_root = os.path.join(os.path.dirname(__file__), "assets")
    _assets = ["time.js"]

    count = hd.Prop(hd.Int, 0)