import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from shapely.geometry import Polygon

# Function to make grid
def make_grid(shapefile, deltax=None, deltay=None):
    """
    deltax & deltay should be measure in meters. standar values: 2000,1000,500
    for EU reglamentations
    """
    xmin, ymin, xmax, ymax = shapefile.total_bounds # extraigo el bounding box del SHAPEFILE
    if deltax == deltay == None:
        # # # # ####################### INI: esta parte es para pruebas ###################
        # # # # # el verdadero dx y dy se definiran en metros segun los arg de entrada
        ncajas = 10                     # defino una cant de cajas para ir jugando
        deltax = (xmax-xmin)/ncajas         # defino el paso X simple solo para ir jugando
        deltay = (ymax-ymin)/ncajas         # defino el paso Y simple solo para ir jugando
        # # # # ####################### FIN: esta parte es de entrenamiento ###################
    cols = np.arange(int(np.floor(xmin)), int(np.ceil(xmax)), deltax)
    rows = np.arange(int(np.floor(ymin)), int(np.ceil(ymax)), deltay)
    poligonos = []
    for x in cols:
        for y in rows:
            poligonos.append(Polygon([ (x,y), (x+deltax,y), (x+deltax,y+deltay), (x,y+deltay) ]))
    rejilla = gpd.GeoDataFrame({'geometry':poligonos}, crs=shapefile.crs)
    return rejilla

def create_grid_place(sitio,cell_size):
    # Now we read the information about CENSUS in balearic islands
    name = sitio

    if sitio == "bal":
        name = "Baleares"
    elif sitio == "mad":
        name = "Madrid"
    else:
        name = "Barcelona" 

    path_palma = './DATA/shapefile/ESP_adm4.shp'
    shp = gpd.read_file(path_palma, geometry='geometry').dissolve(by="NAME_2").reset_index().filter(["NAME_2","geometry"])
    shp = shp.to_crs('epsg:3035')
    shp = shp[shp["NAME_2"] == name]

    # We make grid 2000 x 2000 
    grid = make_grid(shp, deltax=2000, deltay=2000)
    grid = gpd.sjoin(grid,shp, how='inner').reset_index().drop(columns=["index","index_right"]).reset_index()
    grid = grid.rename(columns={"index":"index_cell"})
    print("Number of cells 2000 x 2000: ",len(grid))

    if cell_size < 2000:
        # And a smaller grid 1000 x 1000
        grid_500 = make_grid(grid, deltax=1000, deltay=1000)
        grid_500 = gpd.sjoin(grid_500, grid, how='inner',predicate="within").reset_index().drop(columns=["index","index_right","index_cell"]).reset_index()
        grid_500 = grid_500.rename(columns={"index":"index_cell"})
        print("Number of cells 1000 x 1000: ",len(grid_500))
        
        if cell_size < 1000:
            # And a even smaller grid 500 x 500
            grid_250 = make_grid(grid_500, deltax=500, deltay=500)
            grid_250 = gpd.sjoin(grid_250, grid_500, how='inner',predicate="within").reset_index().drop(columns=["index","index_right","index_cell"]).reset_index()
            grid_250 = grid_250.rename(columns={"index":"index_cell"})
            print("Number of cells 500 x 500: ",len(grid_250))
            grid = grid_250
        else:
            grid = grid_500
    return grid