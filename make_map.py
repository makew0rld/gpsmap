import pickle
import sys
import sqlite3
import time

# This has to be before the other prettymapp imports
import prettymapp.settings

prettymapp.settings.LC_SETTINGS = {
    "water": {
        "natural": ["water", "bay"],
        "place": ["sea"],
    },
    "woodland": {"landuse": ["forest"]},
    "grassland": {
        "landuse": ["grass"],
        "leisure": ["park"],
        "natural": ["wood"],
    },
    "streets": {
        "highway": [
            "motorway",
            "trunk",
            "primary",
        ],
        "railway": True,
    },
}

from prettymapp.geo import get_aoi
from prettymapp.osm import get_osm_geometries
from prettymapp.plotting import Plot
from matplotlib.patches import Ellipse, Rectangle

# Adapted from prettymapp.settings.STYLES["Peach"]
STYLE = {
    # I think this is for buildings and isn't used in my map
    "urban": {
        "cmap": ["#FFC857", "#E9724C", "#C5283D"],
        "ec": "#2F3737",
        "lw": 0,  # 0.5,
        "zorder": 1,
    },
    "water": {
        "fc": "#a1e3ff",
        "ec": "#85c9e6",
        "hatch": "ooo...",
        "hatch_c": "#2F3737",
        "lw": 0,
        "zorder": 3,  # Must be higher than grassland/woodland
    },
    "grassland": {"fc": "#befa9d", "ec": "#2F3737", "lw": 0, "zorder": 2},
    "woodland": {"fc": "#befa9d", "ec": "#2F3737", "lw": 0, "zorder": 2},
    "streets": {"fc": "#7d8686", "zorder": 3},
    "other": {"fc": "#F2F4CB", "ec": "#2F3737", "lw": 0, "zorder": 1},
}

if len(sys.argv) > 1 and sys.argv[1] == "nocache":
    aoi = get_aoi(
        coordinates=(43.703863157620106, -79.39307023501686),
        radius=18000,
        rectangular=True,
    )
    df = get_osm_geometries(aoi=aoi)
    # print(df.total_bounds)
    # print(aoi.bounds)

    plot = Plot(df=df, aoi_bounds=aoi.bounds, draw_settings=STYLE)

    # Plot map background manually to disable hatching
    # Adapted from plot.set_background()
    patch = Rectangle(
        xy=(plot.xmin - plot.bg_buffer_x, plot.ymin - plot.bg_buffer_y),
        width=plot.xdif + 2 * plot.bg_buffer_x,
        height=plot.ydif + 2 * plot.bg_buffer_y,
        color=plot.bg_color,
        zorder=-1,
        clip_on=True,
    )
    plot.ax.add_patch(patch)
    plot.ax.patch.set_zorder(-1)

    # Manually plot map elements, adapted from plot.plot_all()
    plot.set_geometries()
    if plot.contour_width:
        plot.set_map_contour()
    if plot.name_on:
        plot.set_name()

    with open("plot.pickle", "wb") as f:
        pickle.dump(plot, f)

else:
    with open("plot.pickle", "rb") as f:
        plot = pickle.load(f)


# Add manual map elements to image using plot.ax (matplotlib.axes.Axes)

aspect = plot.ax.get_aspect()  # Vertical stretch

con = sqlite3.connect("points.db", autocommit=False)
cur = con.cursor()

# 12 months ago
start_time = int(time.time() - 86400 * 365)

for point in cur.execute(
    "SELECT lat, lon FROM points WHERE time > ?", (start_time,)
).fetchall():
    plot.ax.add_patch(
        Ellipse(
            (point[1], point[0]),
            width=0.001,
            height=0.001 / aspect,
            color="blue",
            fill=True,
            zorder=999,
            alpha=0.5,
            linewidth=0,
        )
    )

cur.close()
con.close()

plot.fig.savefig("map.jpg")
