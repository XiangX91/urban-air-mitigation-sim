import geopandas as gpd
import numpy as np
import xarray as xr
from rasterio import features
import affine
import matplotlib.pyplot as plt
from shapely.validation import make_valid

# === Step 1: Load GeoJSON (with multipolygons) ===
geojson_path = "eer.geojson"  # Adjust if needed
gdf = gpd.read_file(geojson_path)

# === Step 2: Validate and convert geometries if needed ===
# Apply make_valid to fix problematic geometries
gdf["geometry"] = gdf["geometry"].apply(
    lambda geom: make_valid(geom) if geom is not None else None
)

# Explode MultiPolygons to individual polygons
gdf = gdf.explode(index_parts=False).reset_index(drop=True)
gdf = gdf[gdf.is_valid]  # Keep only valid ones

# Ensure CRS is set and reproject to WGS84 (SHERPA grid)
if gdf.crs is None:
    gdf.set_crs(epsg=4326, inplace=True)
else:
    gdf = gdf.to_crs(epsg=4326)

# === Step 3: Define SHERPA grid (Europe-wide) ===
lon = np.arange(-15.05, 36.95 + 0.1, 0.1)
lat = np.arange(32.475, 70.975 + 0.05, 0.05)
transform = affine.Affine(0.1, 0, -15.05, 0, 0.05, 32.475)

# === Step 4: Rasterize all geometries ===
mask = features.rasterize(
    [(geom, 1) for geom in gdf.geometry],
    out_shape=(len(lat), len(lon)),
    transform=transform,
    fill=0,
    dtype="uint8"
)

# === Step 5: Create and save NetCDF file ===
ds = xr.Dataset(
    data_vars={"AREA": (("latitude", "longitude"), mask)},
    coords={"latitude": lat, "longitude": lon}
)

output_file = "emiRedOn_01033_CustomRegion_FUA.nc"
ds.to_netcdf(output_file)
print(f"✅ NetCDF file saved: {output_file}")

# === Optional: Plot to visually confirm ===
def plot_zoomed_mask(nc_path, variable="AREA", padding_lon=0.2, padding_lat=0.1, figsize=(8, 6)):
    """
    Plot a zoomed-in view of a SHERPA-compatible NetCDF mask.

    Parameters:
    - nc_path (str): Path to the .nc file
    - variable (str): Variable name to plot (default is "AREA")
    - padding_lon (float): Extra degrees to pad longitude view
    - padding_lat (float): Extra degrees to pad latitude view
    - figsize (tuple): Figure size for matplotlib
    """
    # Load the NetCDF file
    ds = xr.open_dataset(nc_path)
    data = ds[variable]

    # Find bounding box of non-zero cells
    nonzero = np.nonzero(data.values)
    if len(nonzero[0]) == 0:
        raise ValueError("No non-zero values found in the mask.")

    lat_vals = ds.latitude.values
    lon_vals = ds.longitude.values

    lat_min = lat_vals[np.min(nonzero[0])]
    lat_max = lat_vals[np.max(nonzero[0])]
    lon_min = lon_vals[np.min(nonzero[1])]
    lon_max = lon_vals[np.max(nonzero[1])]

    # Plot
    plt.figure(figsize=figsize)
    data.plot(cmap="Greens")
    plt.title(f"Zoomed View: {variable} Mask")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.xlim(lon_min - padding_lon, lon_max + padding_lon)
    plt.ylim(lat_min - padding_lat, lat_max + padding_lat)
    plt.grid(True)
    plt.show()

plot_zoomed_mask("emiRedOn_01033_CustomRegion_FUA.nc")

