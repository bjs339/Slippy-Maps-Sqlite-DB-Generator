# Slippy Maps Sqlite Database Generator
Creates a sqlite database using the Slippy naming convention from input image with world file. Can be used to create an offline map for Locus from any scanned image. Requires image to be georeferenced against Web Mercator and have a world
file.


## Usage
To prepare image, scan and georeference against a Web Mercator background. Save world file.

Then, run this utility to produre sqlite database files.

Copy output file to Locus offline maps directory on internal store at \Locus\maps.

Assumptions:
* Image is unprojected and rectified against a Web Mercator backdrop, producing a world file that uses Web Mercator units.
* Image is not rotated.


## To Do
* Use temp filename so input doesn't get overwritten/deleted in png
* It appears that Locus isn't honoring the transparent layer
* Make object-oriented, with classes, properties, and static methods where appropriate
* Add support for unprojected WGS84
* Mosiac multiple images into a single map
* Additional output formats
    + Slippy folder system
    + MBTiles


## Credits
This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.

* Cookiecutter: https://github.com/audreyr/cookiecutter
* `audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

Tile calculation functions from GDAL2Tiles

* GDAL2Tiles Project Site: http://www.klokan.cz/projects/gdal2tiles/
* Python script source: http://www.maptiler.org/google-maps-coordinates-tile-bounds-projection/globalmaptiles.py

