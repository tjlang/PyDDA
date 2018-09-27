#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import matplotlib.pyplot as plt
import pyart
import numpy as np
import cartopy.crs as ccrs
import cartopy

from .. import retrieval


def plot_horiz_xsection_barbs(Grids, ax=None, 
                              background_field='reflectivity', level=1,
                              cmap='pyart_LangRainbow12', 
                              vmin=None, vmax=None, 
                              u_vel_contours=None,
                              v_vel_contours=None,
                              w_vel_contours=None,
                              u_field='u', v_field='v', w_field='w',
                              show_lobes=True, title_flag=True, 
                              axes_labels_flag=True, colorbar_flag=True,
                              bg_grid_no=0, barb_spacing_x_km=10.0,
                              barb_spacing_y_km=10.0,
                              contour_alpha=0.7):
    """  
    This procedure plots a horizontal cross section of winds from wind fields
    generated by PyDDA.
    
    Parameters
    ----------
    Grids: list
        List of Py-ART Grids to visualize
    ax: matplotlib axis handle
        The axis handle to place the plot on. Set to None to plot on the 
        current axis.
    background_field: str
        The name of the background field to plot the windbarbs on.
    level: int
        The number of the vertical level to plot the cross section through.
    cmap: str or matplotlib colormap
        The name of the matplotlib colormap to use for the background field.
    vmin: float
        The minimum bound to use for plotting the background field. None will
        automatically detect the background field minimum.
    vmax: float
        The maximum bound to use for plotting the background field. None will
        automatically detect the background field maximum.
    u_vel_contours: 1-D array
        The contours to use for plotting contours of u. Set to None to not 
        display such contours.
    v_vel_contours: 1-D array
        The contours to use for plotting contours of v. Set to None to not 
        display such contours.    
    w_vel_contours: 1-D array
        The contours to use for plotting contours of w. Set to None to not 
        display such contours.    
    u_field: str
        Name of zonal wind (u) field in Grids.     
    v_field: str
        Name of zonal wind (v) field in Grids.         
    w_field: str
        Name of zonal wind (w) field in Grids.         
    show_lobes: bool
        If True, the dual doppler lobes from each pair of radars will be shown.
    title_flag: bool
        If True, PyDDA will generate a title for the plot.
    axes_labels_flag: bool
        If True, PyDDA will generate axes labels for the plot
    colorbar_flag: bool
        If True, PyDDA will generate a colorbar for the plot
    bg_grid_no: int
        Number of grid in Grids to take background field from.
        Set to -1 to use maximum value from all grids.
    barb_spacing_x_km: float
        The spacing in km between each wind barb in the x direction.
    barb_spacing_y_km: float
        The spacing in km between each wind barb in the y direction.   
    contour_alpha: float
        Alpha (transparency) of velocity contours. 0 = transparent, 1 = opaque
    Returns
    -------
    Nothing
    """
    
    if(bg_grid_no > -1):
        grid_bg = Grids[bg_grid_no].fields[background_field]['data']
    else:
        grid_array = np.ma.stack([x.fields[background_field]['data'] for x in Grids])
        grid_bg = grid_array.max(axis=0)

    
    if(vmin == None):
        vmin = grid_bg.min()
        
    if(vmax == None):
        vmax = grid_bg.max()
        
    grid_h = Grids[0].point_altitude['data']/1e3
    grid_x = Grids[0].point_x['data']/1e3
    grid_y = Grids[0].point_y['data']/1e3
    dx = np.diff(grid_x, axis=2)[0,0,0]
    dy = np.diff(grid_y, axis=1)[0,0,0]
    u = Grids[0].fields[u_field]['data']
    v = Grids[0].fields[v_field]['data']
    w = Grids[0].fields[w_field]['data']
    
    if(ax == None):
        ax = plt.gca()
    
    the_mesh = ax.pcolormesh(grid_x[level,::,::], grid_y[level,::,::], 
                             grid_bg[level,:,:],
                   cmap=cmap)
    barb_density_x = int((dx)*barb_spacing_x_km)
    barb_density_y = int((dy)*barb_spacing_y_km)
    ax.barbs(grid_x[level,::barb_density_y,::barb_density_x], 
              grid_y[level,::barb_density_y,::barb_density_x], 
              u[level,::barb_density_y,::barb_density_x], 
              v[level,::barb_density_y,::barb_density_x])
    
    if(colorbar_flag == True):
        cp = Grids[bg_grid_no].fields[background_field]['long_name']
        cp.replace(' ', '_')
        cp = cp + ' [' + Grids[bg_grid_no].fields[background_field]['units']
        cp = cp + ']'
        plt.colorbar(the_mesh, ax=ax, label=(cp))
    
    if(u_vel_contours is not None):
        u_filled = np.ma.filled(u[level,::,::], fill_value=0)
        cs = ax.contour(grid_x[level,::,::], grid_y[level,::,::],
                         u_filled, levels=u_vel_contours, linewidths=2, 
                         alpha=contour_alpha)
        ax.clabel(cs)
    
    if(v_vel_contours is not None):
        v_filled = np.ma.filled(v[level,::,::], fill_value=0)
        cs = ax.contour(grid_x[level,::,::], grid_y[level,::,::],
                         v_filled, levels=u_vel_contours, linewidths=2, 
                         alpha=contour_alpha)
        ax.clabel(cs)    
        
    if(w_vel_contours is not None):
        w_filled = np.ma.filled(w[level,::,::], fill_value=0)
        cs = ax.contour(grid_x[level,::,::], grid_y[level,::,::],
                         w_filled, levels=w_vel_contours, linewidths=2, 
                         alpha=contour_alpha)
        ax.clabel(cs)

        
    bca_min = math.radians(Grids[0].fields[u_field]['min_bca'])
    bca_max = math.radians(Grids[0].fields[u_field]['max_bca'])
    
    if(show_lobes is True):
        for i in range(len(Grids)):
            for j in range(len(Grids)):
                if (i != j):
                    bca = retrieval.get_bca(Grids[j].radar_longitude['data'],
                                            Grids[j].radar_latitude['data'],
                                            Grids[i].radar_longitude['data'], 
                                            Grids[i].radar_latitude['data'],
                                            Grids[j].point_x['data'][0],
                                            Grids[j].point_y['data'][0],
                                            Grids[j].get_projparams())
                    
                    ax.contour(
                        grid_x[level,::,::], grid_y[level,::,::], bca,
                        levels=[bca_min, bca_max], color='k')
               
    
    if(axes_labels_flag == True):
        ax.set_xlabel(('X [km]'))
        ax.set_ylabel(('Y [km]'))
    
    if(title_flag == True):
        ax.set_title(
            ('PyDDA retreived winds @' + str(grid_h[level,0,0]) + ' km'))

             
        
    ax.set_xlim([grid_x.min(), grid_x.max()])
    ax.set_ylim([grid_y.min(), grid_y.max()])
    
        
def plot_horiz_xsection_barbs_map(Grids, ax=None, 
                              background_field='reflectivity', 
                              level=1,
                              cmap='pyart_LangRainbow12', 
                              vmin=None, vmax=None, 
                              u_vel_contours=None,
                              v_vel_contours=None,
                              w_vel_contours=None,
                              u_field='u', v_field='v', w_field='w',
                              show_lobes=True, title_flag=True, 
                              axes_labels_flag=True, colorbar_flag=True,
                              bg_grid_no=0, barb_spacing_x_km=10.0,
                              barb_spacing_y_km=10.0,
                              contour_alpha=0.7,
                              coastlines=True,
                              gridlines=True,
                              ):
    """  
    This procedure plots a horizontal cross section of winds from wind fields
    generated by PyDDA.
    
    Parameters
    ----------
    Grids: list
        List of Py-ART Grids to visualize
    ax: matplotlib axis handle (with cartopy ccrs)
        The axis handle to place the plot on. Set to None to create a new map.
    Note: the axis needs to be in a PlateCarree() projection.
    background_field: str
        The name of the background field to plot the windbarbs on.
    level: int
        The number of the vertical level to plot the cross section through.
    cmap: str or matplotlib colormap
        The name of the matplotlib colormap to use for the background field.
    vmin: float
        The minimum bound to use for plotting the background field. None will
        automatically detect the background field minimum.
    vmax: float
        The maximum bound to use for plotting the background field. None will
        automatically detect the background field maximum.
    u_vel_contours: 1-D array
        The contours to use for plotting contours of u. Set to None to not 
        display such contours.
    v_vel_contours: 1-D array
        The contours to use for plotting contours of v. Set to None to not 
        display such contours.    
    w_vel_contours: 1-D array
        The contours to use for plotting contours of w. Set to None to not 
        display such contours.    
    u_field: str
        Name of zonal wind (u) field in Grids.     
    v_field: str
        Name of zonal wind (v) field in Grids.         
    w_field: str
        Name of zonal wind (w) field in Grids.         
    show_lobes: bool
        If True, the dual doppler lobes from each pair of radars will be shown.
    title_flag: bool
        If True, PyDDA will generate a title for the plot.
    axes_labels_flag: bool
        If True, PyDDA will generate axes labels for the plot
    colorbar_flag: bool
        If True, PyDDA will generate a colorbar for the plot
    bg_grid_no: int
        Number of grid in Grids to take background field from.
        Set to -1 to use maximum value from all grids.
    barb_spacing_x_km: float
        The spacing in km between each wind barb in the x direction.
    barb_spacing_y_km: float
        The spacing in km between each wind barb in the y direction.   
    contour_alpha: float
        Alpha (transparency) of velocity contours. 0 = transparent, 1 = opaque
    coastlines: bool
        Set to true to display coastlines
    gridlines: bool
        Set to true to show grid lines.
    Returns
    -------
    Nothing
    """
    
    if(bg_grid_no > -1):
        grid_bg = Grids[bg_grid_no].fields[background_field]['data']
    else:
        grid_array = np.ma.stack([x.fields[background_field]['data'] for x in Grids])
        grid_bg = grid_array.max(axis=0)

    
    if(vmin == None):
        vmin = grid_bg.min()
        
    if(vmax == None):
        vmax = grid_bg.max()
        
    grid_h = Grids[0].point_altitude['data']/1e3
    grid_x = Grids[0].point_x['data']/1e3
    grid_y = Grids[0].point_y['data']/1e3
    grid_lat = Grids[0].point_latitude['data'][level]
    grid_lon = Grids[0].point_longitude['data'][level]
    
    dx = np.diff(grid_x, axis=2)[0,0,0]
    dy = np.diff(grid_y, axis=1)[0,0,0]
    u = Grids[0].fields[u_field]['data']
    v = Grids[0].fields[v_field]['data']
    w = Grids[0].fields[w_field]['data']

    transform = ccrs.PlateCarree()
    if(ax == None):
        ax = plt.axes(projection=transform)
    
    the_mesh = ax.pcolormesh(grid_lon[::,::], grid_lat[::,::], 
                             grid_bg[level,:,:],
                             cmap=cmap, transform=transform, zorder=0)
    barb_density_x = int((dx)*barb_spacing_x_km)
    barb_density_y = int((dy)*barb_spacing_y_km)
    
    ax.barbs(grid_lon[::barb_density_y,::barb_density_x], 
              grid_lat[::barb_density_y,::barb_density_x], 
              u[level,::barb_density_y,::barb_density_x], 
              v[level,::barb_density_y,::barb_density_x],
              transform=transform, zorder=1)
    
    if(colorbar_flag == True):
        cp = Grids[bg_grid_no].fields[background_field]['long_name']
        cp.replace(' ', '_')
        cp = cp + ' [' + Grids[bg_grid_no].fields[background_field]['units']
        cp = cp + ']'
        plt.colorbar(the_mesh, ax=ax, label=(cp))
    
    if(u_vel_contours is not None):
        u_filled = np.ma.filled(u[level,::,::], fill_value=0)
        cs = ax.contour(grid_lon[::,::], grid_lat[::,::],
                         u_filled, levels=u_vel_contours, linewidths=2, 
                         alpha=contour_alpha, zorder=2)
        ax.clabel(cs)
    
    if(v_vel_contours is not None):
        v_filled = np.ma.filled(v[level,::,::], fill_value=0)
        cs = ax.contour(grid_lon[::,::], grid_lat[::,::],
                         v_filled, levels=u_vel_contours, linewidths=2, 
                         alpha=contour_alpha, zorder=2)
        ax.clabel(cs)    
        
    if(w_vel_contours is not None):
        w_filled = np.ma.filled(w[level,::,::], fill_value=0)
        cs = ax.contour(grid_lon[::,::], grid_lat[::,::],
                         w_filled, levels=w_vel_contours, linewidths=2, 
                         alpha=contour_alpha, zorder=2)
        ax.clabel(cs)

        
    bca_min = math.radians(Grids[0].fields[u_field]['min_bca'])
    bca_max = math.radians(Grids[0].fields[u_field]['max_bca'])
    
    if(show_lobes is True):
        for i in range(len(Grids)):
            for j in range(len(Grids)):
                if (i != j):
                    bca = retrieval.get_bca(Grids[j].radar_longitude['data'],
                                            Grids[j].radar_latitude['data'],
                                            Grids[i].radar_longitude['data'], 
                                            Grids[i].radar_latitude['data'],
                                            Grids[j].point_x['data'][0],
                                            Grids[j].point_y['data'][0],
                                            Grids[j].get_projparams())
                    
                    ax.contour(
                        grid_lon[::,::], grid_lat[::,::], bca,
                        levels=[bca_min, bca_max], color='k', zorder=1)
               
    
    if(axes_labels_flag == True):
        ax.set_xlabel(('X [km]'))
        ax.set_ylabel(('Y [km]'))
    
    if(title_flag == True):
        ax.set_title(
            ('PyDDA retreived winds @' + str(grid_h[level,0,0]) + ' km'))
                   
    if(coastlines == True):
        ax.coastlines(resolution='10m')
        
    if(gridlines == True):
        ax.gridlines()      
    ax.set_extent([grid_lon.min(), grid_lon.max(), 
                   grid_lat.min(), grid_lat.max()])    
        
def plot_xz_xsection_barbs(Grids, ax=None,
                           background_field='reflectivity', level=1, 
                           cmap='pyart_LangRainbow12', 
                           vmin=None, vmax=None, u_vel_contours=None,
                           v_vel_contours=None, w_vel_contours=None,
                           u_field='u', v_field='v', w_field='w',
                           title_flag=True, axes_labels_flag=True, 
                           colorbar_flag=True,
                           bg_grid_no=0, barb_spacing_x_km=10.0,
                           barb_spacing_z_km=1.0,
                           contour_alpha=0.7):
    """   
    This procedure plots a cross section of winds from wind fields
    generated by PyDDA in the X-Z plane.
    
    Parameters
    ----------
    Grids: list
        List of Py-ART Grids to visualize
    ax: matplotlib axis handle
        The axis handle to place the plot on. Set to None to plot on the 
        current axis.
    background_field: str
        The name of the background field to plot the windbarbs on.
    level: int
        The number of the Y level to plot the cross section through.
    cmap: str or matplotlib colormap
        The name of the matplotlib colormap to use for the background field.
    vmin: float
        The minimum bound to use for plotting the background field. None will
        automatically detect the background field minimum.
    vmax: float
        The maximum bound to use for plotting the background field. None will
        automatically detect the background field maximum.
    u_vel_contours: 1-D array
        The contours to use for plotting contours of u. Set to None to not 
        display such contours.
    v_vel_contours: 1-D array
        The contours to use for plotting contours of v. Set to None to not 
        display such contours.    
    w_vel_contours: 1-D array
        The contours to use for plotting contours of w. Set to None to not 
        display such contours.    
    u_field: str
        Name of zonal wind (u) field in Grids.     
    v_field: str
        Name of zonal wind (v) field in Grids.         
    w_field: str
        Name of zonal wind (w) field in Grids.         
    show_lobes: bool
        If True, the dual doppler lobes from each pair of radars will be shown.
    title_flag: bool
        If True, PyDDA will generate a title for the plot.
    axes_labels_flag: bool
        If True, PyDDA will generate axes labels for the plot
    colorbar_flag: bool
        If True, PyDDA will generate a colorbar for the plot
    bg_grid_no: int
        Number of grid in Grids to take background field from.
    barb_spacing_x_km: float
        The spacing in km between each wind barb in the x direction.
    barb_spacing_z_km: float
        The spacing in km between each wind barb in the z direction.   
        
    Returns
    -------
    Nothing
    """
    
    if(bg_grid_no > -1):
        grid_bg = Grids[bg_grid_no].fields[background_field]['data']
    else:
        grid_array = np.ma.stack([x.fields[background_field]['data'] for x in Grids])
        grid_bg = grid_array.max(axis=0)
    
    if(vmin == None):
        vmin = grid_bg.min()
        
    if(vmax == None):
        vmax = grid_bg.max()
        
    grid_h = Grids[0].point_altitude['data']/1e3
    grid_x = Grids[0].point_x['data']/1e3
    grid_y = Grids[0].point_y['data']/1e3
    dx = np.diff(grid_x, axis=2)[0,0,0]
    dz = np.diff(grid_y, axis=1)[0,0,0]
    u = Grids[0].fields[u_field]['data']
    v = Grids[0].fields[v_field]['data']
    w = Grids[0].fields[w_field]['data']
    
    if(ax == None):
        ax = plt.gca()
        
    the_mesh = ax.pcolormesh(grid_x[:,level,:], grid_h[:,level,:], 
                             grid_bg[:,level,:],
                   cmap=cmap)
    barb_density_x = int((dx)*barb_spacing_x_km)
    barb_density_z = int((dz)*barb_spacing_z_km)
    ax.barbs(grid_x[::barb_density_z,level,::barb_density_x], 
              grid_h[::barb_density_z,level,::barb_density_x], 
              u[::barb_density_z,level,::barb_density_x], 
              w[::barb_density_z,level,::barb_density_x])
    
    if(colorbar_flag == True):
        cp = Grids[bg_grid_no].fields[background_field]['long_name']
        cp.replace(' ', '_')
        cp = cp + ' [' + Grids[bg_grid_no].fields[background_field]['units'] 
        cp = cp + ']'
        plt.colorbar(the_mesh, ax=ax, label=(cp))
        
    if(u_vel_contours is not None):
        u_filled = np.ma.filled(u[::,level,::], fill_value=0)
        cs = ax.contour(grid_x[::,level,::], grid_h[::,level,::],
                         u_filled, levels=u_vel_contours, linewidths=2, 
                         alpha=contour_alpha)
        ax.clabel(cs)
        
    if(v_vel_contours is not None):
        v_filled = np.ma.filled(w[::,level,::], fill_value=0)
        cs = ax.contour(grid_x[::,level,::], grid_h[::,level,::],
                         v_filled, levels=v_vel_contours, linewidths=2, 
                         alpha=contour_alpha)
        ax.clabel(cs)    
    
    if(w_vel_contours is not None):
        w_filled = np.ma.filled(w[::,level,::], fill_value=0)
        cs = ax.contour(grid_x[::,level,::], grid_h[::,level,::],
                         w_filled, levels=w_vel_contours, linewidths=2, 
                         alpha=contour_alpha)
        ax.clabel(cs)
  
    
    if(axes_labels_flag == True):
        ax.set_xlabel(('X [km]'))
        ax.set_ylabel(('Z [km]'))
    
    if(title_flag == True):
        if(grid_y[0,level,0] > 0):
            ax.set_title(('PyDDA retreived winds @' + str(grid_y[0,level,0]) + 
                          ' km north of origin.'))
        else:
            ax.set_title(('PyDDA retreived winds @' + str(-grid_y[0,level,0]) + 
                          ' km south of origin.'))
        
    ax.set_xlim([grid_x.min(), grid_x.max()])
    ax.set_ylim([grid_h.min(), grid_h.max()])


def plot_yz_xsection_barbs(Grids, ax=None,
                           background_field='reflectivity', level=1, 
                           cmap='pyart_LangRainbow12', 
                           vmin=None, vmax=None, u_vel_contours=None,
                           v_vel_contours=None, w_vel_contours=None,
                           u_field='u', v_field='v', w_field='w',
                           title_flag=True, axes_labels_flag=True, 
                           colorbar_flag=True,
                           bg_grid_no=0, barb_spacing_y_km=10.0,
                           barb_spacing_z_km=1.0,
                           contour_alpha=0.7):


    """
    This procedure plots a cross section of winds from wind fields
    generated by PyDDA in the Y-Z plane.
    
    Parameters
    ----------
    Grids: list
        List of Py-ART Grids to visualize
    ax: matplotlib axis handle
        The axis handle to place the plot on. Set to None to plot on the 
        current axis.
    background_field: str
        The name of the background field to plot the windbarbs on.
    level: int
        The number of the X level to plot the cross section through.
    cmap: str or matplotlib colormap
        The name of the matplotlib colormap to use for the background field.
    vmin: float
        The minimum bound to use for plotting the background field. None will
        automatically detect the background field minimum.
    vmax: float
        The maximum bound to use for plotting the background field. None will
        automatically detect the background field maximum.
    u_vel_contours: 1-D array
        The contours to use for plotting contours of u. Set to None to not 
        display such contours.
    v_vel_contours: 1-D array
        The contours to use for plotting contours of v. Set to None to not 
        display such contours.    
    w_vel_contours: 1-D array
        The contours to use for plotting contours of w. Set to None to not 
        display such contours.    
    u_field: str
        Name of zonal wind (u) field in Grids.     
    v_field: str
        Name of zonal wind (v) field in Grids.         
    w_field: str
        Name of zonal wind (w) field in Grids.         
    show_lobes: bool
        If True, the dual doppler lobes from each pair of radars will be shown.
    title_flag: bool
        If True, PyDDA will generate a title for the plot.
    axes_labels_flag: bool
        If True, PyDDA will generate axes labels for the plot
    colorbar_flag: bool
        If True, PyDDA will generate a colorbar for the plot
    bg_grid_no: int
        Number of grid in Grids to take background field from.
    barb_spacing_y_km: float
        The spacing in km between each wind barb in the y direction.
    barb_spacing_z_km: float
        The spacing in km between each wind barb in the z direction.   
        
    Returns
    -------
    Nothing
    """
    
    if(bg_grid_no > -1):
        grid_bg = Grids[bg_grid_no].fields[background_field]['data']
    else:
        grid_array = np.ma.stack([x.fields[background_field]['data'] for x in Grids])
        grid_bg = grid_array.max(axis=0)
    
    if(vmin == None):
        vmin = grid_bg.min()
        
    if(vmax == None):
        vmax = grid_bg.max()
        
    grid_h = Grids[0].point_altitude['data']/1e3
    grid_x = Grids[0].point_x['data']/1e3
    grid_y = Grids[0].point_y['data']/1e3
    dx = np.diff(grid_x, axis=2)[0,0,0]
    dz = np.diff(grid_y, axis=1)[0,0,0]
    u = Grids[0].fields[u_field]['data']
    v = Grids[0].fields[v_field]['data']
    w = Grids[0].fields[w_field]['data']
    
    if(ax == None):
        ax = plt.gca()
        
    the_mesh = ax.pcolormesh(grid_y[::,::,level], grid_h[::,::,level], 
                  grid_bg[::,::,level], cmap=cmap)
    barb_density_x = int((dx)*barb_spacing_y_km)
    barb_density_z = int((dz)*barb_spacing_z_km)
    ax.barbs(grid_y[::barb_density_z,::barb_density_x, level], 
              grid_h[::barb_density_z,::barb_density_x, level], 
              v[::barb_density_z,::barb_density_x, level], 
              w[::barb_density_z,::barb_density_x, level])
    
    if(colorbar_flag == True):
        cp = Grids[bg_grid_no].fields[background_field]['long_name']
        cp.replace(' ', '_')
        cp = cp + ' [' + Grids[bg_grid_no].fields[background_field]['units'] 
        cp = cp + ']'
        plt.colorbar(the_mesh, ax=ax, label=(cp))
    
    if(u_vel_contours is not None):
        u_filled = np.ma.filled(u[::,::,level], fill_value=0)
        cs = plt.contour(grid_y[::, ::, level], grid_h[::, ::, level],
                         u_filled, levels=u_vel_contours, linewidths=2, 
                         alpha=contour_alpha)
        plt.clabel(cs)
    
    if(v_vel_contours is not None):
        v_filled = np.ma.filled(v[::,::,level], fill_value=0)
        cs = plt.contour(grid_y[::, ::, level], grid_h[::, ::, level],
                         v_filled, levels=w_vel_contours, linewidths=2, 
                         alpha=contour_alpha)
        plt.clabel(cs)    
        
    if(w_vel_contours is not None):
        w_filled = np.ma.filled(w[::,::,level], fill_value=0)
        cs = plt.contour(grid_y[::, ::, level], grid_h[::, ::, level],
                         w_filled, levels=w_vel_contours, linewidths=2, 
                         alpha=contour_alpha)
        plt.clabel(cs)

    
    if(axes_labels_flag == True):
        ax.set_xlabel(('Y [km]'))
        ax.set_ylabel(('Z [km]'))
    
    if(title_flag == True):
        if(grid_x[0,0, level] > 0):
            ax.set_title(('PyDDA retreived winds @' + str(grid_x[0,0,level]) +
                         ' km east of origin.'))
        else:
            ax.set_title(('PyDDA retreived winds @' + str(-grid_x[0,0,level]) +
                          ' km west of origin.'))
        
    ax.set_xlim([grid_y.min(), grid_y.max()])
    ax.set_ylim([grid_h.min(), grid_h.max()])
        
                
