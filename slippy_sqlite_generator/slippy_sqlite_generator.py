# -*- coding: utf-8 -*-


import os
import PIL
from PIL import Image
import sqlite3
import math
from .globalmercator import GlobalMercator


# Partial list of some possible world file extensions
world_file_ext = {
    '.jpg': ['.jgw', '.jpgw', 'jgwx'],
    '.tif': ['.tfw', '.tifw'],
    '.sid': ['.sdw'],
    '.bmp': ['.bpw'],
    '.png': ['.pgw', '.pngw', '.pgwx']
}

# http://wiki.openstreetmap.org/wiki/Zoom_levels
meters_per_pixel = {
    0: 156412,
    1: 78206,
    2: 39103,
    3: 19551,
    4: 9776,
    5: 4888,
    6: 2444,
    7: 1222,
    8: 610.984,
    9: 305.492,
    10: 152.746,
    11: 76.373,
    12: 38.187,
    13: 19.093,
    14: 9.547,
    15: 4.773,
    16: 2.387,
    17: 1.193,
    18: 0.596,
    19: 0.298
}


class SlippySqliteGenerator:

    def __init__(self, image_file_path, output_database):
        self.image_file_path = image_file_path
        self.output_database = output_database
        self.gm = GlobalMercator()

    def process(self):
        workspace = os.path.dirname(self.image_file_path)

        # Read the world file
        f, e = os.path.splitext(self.image_file_path)
        for ext in world_file_ext[e]:
            if os.path.isfile("{}{}".format(f, ext)):
                world_file = "{}{}".format(f, ext)
                break

        if 'world_file' not in vars():
            raise Exception

        try:
            with open(world_file, 'r') as world_file:
                x_cell_size = float(world_file.readline())
                x_rotation = world_file.readline()
                y_rotation = world_file.readline()
                y_cell_size = float(world_file.readline())
                x_anchor = float(world_file.readline())
                y_anchor = float(world_file.readline())
        except Exception:
            # print("Error opening world file")
            pass

        # Create the database and table
        try:
            os.remove(os.path.join(workspace, self.output_database))
        except OSError:
            pass

        conn = sqlite3.connect(os.path.join(workspace, self.output_database))
        c = conn.cursor()
        c.execute(
            'CREATE TABLE tiles (x INTEGER, y INTEGER, z INTEGER, s INTEGER, '
            'image BYTE, PRIMARY KEY (x, y, z))')
        conn.commit()
        conn.close()

        # Resample the image to match the resolution of the target zoom level
        # Open the image
        image = Image.open(self.image_file_path)
        (x0_image_bbox, y0_image_bbox, x1_image_bbox, y1_image_bbox) = image.getbbox()

        zoom = self.gm.ZoomForPixelSize(x_cell_size)
        # Locus seems to want the zoom values inverted, so...
        locus_zoom = 17 - zoom

        # Get the image values for the zoom level
        target_mpp = meters_per_pixel[zoom]
        target_width = int(math.ceil(math.fabs(x1_image_bbox * x_cell_size / target_mpp)))
        target_height = int(math.ceil(math.fabs(y1_image_bbox * y_cell_size / target_mpp)))

        # Convert the image file to png
        f, e = os.path.splitext(self.image_file_path)
        converted_image_path = "temp.png"
        image.save(converted_image_path)
        image.close()

        # Resize the image to the correct resolution for the zoom level at the same time
        temp_image = Image.open(converted_image_path)
        temp_image = temp_image.resize((target_width, target_height), PIL.Image.BILINEAR)

        # Calculate what tile the top-left corner is in
        (lat, lon) = self.gm.MetersToLatLon(x_anchor, y_anchor)
        (x_tile, y_tile) = self.deg2num(lat, lon, zoom)

        # We need to pad the top left so we start at the top-left corner of the tile
        (x_pixels_padding, y_pixels_padding) = self.getPixelPadding(x_anchor, y_anchor, x_tile, y_tile, zoom, target_mpp)

        # Add alpha channel and get background
        (mode, background) = self.setImageMode(temp_image)

        # Pad the image
        padded_image = Image.new(mode, (target_width + x_pixels_padding, target_height + y_pixels_padding), background)
        padded_image.paste(temp_image, (x_pixels_padding, y_pixels_padding))

        conn = sqlite3.connect(os.path.join(workspace, self.output_database))
        c = conn.cursor()

        try:
            # Loop through the zoom levels until you've had enough
            while target_width >= 256 and target_height >= 256:

                # Break the image apart into 256 x 256 png files with georeferencing information and save to db
                x_region_tile = x_tile
                y_region_tile = y_tile
                x0_region_box = 0
                y0_region_box = 0
                x1_region_box = 256
                y1_region_box = 256

                # Loop through the rows
                while y0_region_box < target_height + y_pixels_padding:

                    # Loop through the columns in each row
                    while x0_region_box < target_width + x_pixels_padding:

                        # Crop it
                        box = (x0_region_box, y0_region_box, x1_region_box, y1_region_box)
                        region = padded_image.crop(box)
                        region.save(os.path.join(workspace, '{0}_{1}_{2}.png'.format(zoom, x_region_tile, y_region_tile)))

                        # Save it to the database
                        with open(os.path.join(workspace, '{0}_{1}_{2}.png'.format(zoom, x_region_tile, y_region_tile)), 'rb') as input_file:
                            ablob = input_file.read()
                            sql = "INSERT OR IGNORE INTO tiles (x, y, z, image) VALUES ({x}, {y}, {z}, ?)".format(
                                x=x_region_tile, y=y_region_tile, z=locus_zoom)
                            c.execute(sql, [sqlite3.Binary(ablob)])

                        try:
                            os.remove(os.path.join(workspace, '{0}_{1}_{2}.png'.format(zoom, x_region_tile, y_region_tile)))
                        except OSError:
                            pass

                        # Increment for the next column
                        x_region_tile += 1
                        x0_region_box += 256
                        x1_region_box += 256

                    # Increment for the next row, reset to the first column
                    x_region_tile = x_tile
                    y_region_tile += 1
                    y0_region_box += 256
                    y1_region_box += 256
                    x0_region_box = 0
                    x1_region_box = 256

                # Next zoom level
                zoom -= 1
                locus_zoom = 17 - zoom

                # Get the image values for the zoom level
                target_mpp = meters_per_pixel[zoom]
                target_width = int(math.ceil(math.fabs(x1_image_bbox * x_cell_size / target_mpp)))
                target_height = int(math.ceil(math.fabs(y1_image_bbox * y_cell_size / target_mpp)))

                # Resize the image
                temp_image = Image.open(converted_image_path)
                try:
                    temp_image = temp_image.resize((target_width, target_height), PIL.Image.BILINEAR)
                except IOError:
                    # print("Cannot convert", converted_image_path)
                    pass

                # padded_image.close()

                # Calculate what tile the top-left corner is in
                lat, lon = self.gm.MetersToLatLon(x_anchor, y_anchor)
                (x_tile, y_tile) = self.deg2num(lat, lon, zoom)

                # Create the new image for this zoom level
                (x_pixels_padding, y_pixels_padding) = self.getPixelPadding(x_anchor, y_anchor, x_tile, y_tile, zoom, target_mpp)
                padded_image = Image.new(mode, (target_width + x_pixels_padding, target_height + y_pixels_padding), background)
                padded_image.paste(temp_image, (x_pixels_padding, y_pixels_padding))

                # Reset the bounding box
                x0_image_bbox = 0
                y0_image_bbox = 0
                x1_image_bbox = target_width
                y1_image_bbox = target_height

        except Exception as ex:
            # print("Error")
            pass

        finally:
            try:
                padded_image.close()
                os.remove(converted_image_path)
            except OSError as err:
                pass

            conn.commit()
            conn.close()

        print("Completed")

    # http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers_2
    def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return (xtile, ytile)

    # http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_numbers_to_lon..2Flat._2
    def num2deg(self, xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def setImageMode(self, image):
        # Thank you http://stackoverflow.com/a/27784311
        mode = image.mode
        if len(mode) == 1:  # L, 1
            mode = "LA"
            background = (255, 0)
        if len(mode) == 3:  # RGB
            mode = "RGBA"
            background = (255, 255, 255, 0)
        if len(mode) == 4:  # RGBA
            background = (255, 255, 255, 0)
        return (mode, background)

    def getPixelPadding(self, x_anchor, y_anchor, x_tile, y_tile, zoom, target_mpp):
        # Figure out how much padding to add to the top and left
        (lat_tile, lon_tile) = self.num2deg(x_tile, y_tile, zoom)
        (x_mercator_tile, y_mercator_tile) = self.gm.LatLonToMeters(lat_tile, lon_tile)
        x_meters_padding = x_mercator_tile - x_anchor
        y_meters_padding = y_mercator_tile - y_anchor
        x_pixels_padding = int(math.fabs(math.floor(x_meters_padding / target_mpp)))
        y_pixels_padding = math.floor(y_meters_padding / target_mpp)

        return (x_pixels_padding, y_pixels_padding)
