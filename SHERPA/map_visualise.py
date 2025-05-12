import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def plot_area_mask(area_xr, title="AREA Mask", padding=0.5):
    """Plots a 2D xarray DataArray and zooms to its nonzero extent."""
    lat = area_xr.latitude
    lon = area_xr.longitude
    mask = area_xr.values

    import numpy as np
    mask_bool = mask != 0
    if not np.any(mask_bool):
        print("No nonzero AREA values to plot.")
        return

    lat_idx, lon_idx = np.where(mask_bool)
    lat_vals = lat.values[lat_idx]
    lon_vals = lon.values[lon_idx]

    plt.figure(figsize=(8, 6))
    plt.pcolormesh(lon, lat, mask, cmap='Blues', shading='auto')
    plt.colorbar(label='AREA value')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(title)
    plt.xlim(lon_vals.min() - padding, lon_vals.max() + padding)
    plt.ylim(lat_vals.min() - padding, lat_vals.max() + padding)
    plt.grid(True)
    plt.show()


def plot_concentration_map(data, title, cmap="RdBu_r", cbar_label="ΔConcentration (μg/m³)",
                           extent=[-8.5, 2.5, 49.5, 60.0], figsize=(8, 5)):
    """Plots a 2D concentration map over a UK-wide domain."""
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.PlateCarree()})
    data.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap=cmap,
                         cbar_kwargs={'label': cbar_label})
    ax.coastlines(resolution='10m')
    ax.add_feature(cfeature.BORDERS)
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.set_title(title)
    plt.show()