from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from aviationapp.models import Airports, Taf

import matplotlib
matplotlib.use('Cairo')
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
from cartopy.io import shapereader
import geopandas
from geopy.distance import geodesic
from shapely.geometry import LineString as shLs
from shapely.geometry import Point as shPt
import io, base64
import pandas as pd
import numpy as np


def index(request):
    return HttpResponse("Hello, world. You're at the aviation indexpage.")


def home(request):
    context = {}
    reqfrom = request.POST.get('from') 
    reqto = request.POST.get('to')
    airports_list = get_airports()
    stations_list = get_stations()
    context['graph'] = return_graph(reqfrom, reqto, airports_list, stations_list)
    context['title'] = 'Canadian Stations'
    context['airport_list'] = get_airports().ident.values
    graph2, closest_stations = get_between_stations(reqfrom, reqto, airports_list, stations_list)
    context['graph2'] = graph2
    return render(request, 'dashboard.html', context)


def get_airports():
    airports = pd.DataFrame(list(Airports.objects.all().values('ident', 'type', 'name', 'iso_country', 'longitude_deg', 'latitude_deg')))
    airports = airports.loc[((airports['iso_country']=='CA')) & (airports['type']!='closed')]
    return airports


def get_stations():
    stations = pd.DataFrame(list(Taf.objects.all().values('station_id', 'latitude', 'longitude')))
    return stations


def get_between_stations(reqfrom, reqto, airports_list, stations_list):
    closest_stations = []
    if (reqfrom is not None and reqto is not None):
        
        fig = plt.figure()
        from_loc = airports_list[airports_list.ident == reqfrom]
        to_loc = airports_list[airports_list.ident == reqto]
        from_long = from_loc['longitude_deg'].iloc[0]
        from_lat = from_loc['latitude_deg'].iloc[0]
        to_long = to_loc['longitude_deg'].iloc[0]
        to_lat = to_loc['latitude_deg'].iloc[0]
        
        min_long = min(from_long, to_long)
        max_long = max(from_long, to_long)
        min_lat = min(from_lat, to_lat)
        max_lat = max(from_lat, to_lat)
        
        between_stations = stations_list.loc[
            (stations_list.longitude.astype('float').between(min_long, max_long)) & 
            (stations_list.latitude.astype('float').between(min_lat, max_lat))
        ]
        
        plt.scatter(from_long, from_lat, color='red', s=2
        )
        
        plt.scatter(to_long, to_lat, color='red', s=2
        )

        plt.plot([from_long, to_long], [from_lat, to_lat], 
            color='gray', linestyle='--'
        )

        plt.text(from_long, from_lat, reqfrom,
            horizontalalignment='right', weight='bold', fontsize='small'
        )
    
        plt.text(to_long, to_lat, reqto,
            horizontalalignment='left', weight='bold', fontsize='small'
        )

        l = shLs([ (from_long,from_lat), (to_long,to_lat)])
        ax = plt.gca()

        for _, row in between_stations.iterrows():
            p = shPt(np.float(row['longitude']), np.float(row['latitude']))
            dist = p.distance(l)
            if dist < 1.0:
                plt.scatter(np.float(row['longitude']), np.float(row['latitude']), color='blue', s=2)
                ax.add_patch(plt.Circle((np.float(row['longitude']), np.float(row['latitude'])), 1.5, color='blue', fill=False))
                closest_stations.append(row)

        imgdata = io.BytesIO()
        fig.savefig(imgdata, format='png')
        plt.clf()
        data = base64.b64encode(imgdata.getvalue()).decode()
        return data, closest_stations
    else:
        return None, closest_stations


def return_graph(reqfrom, reqto, airports_list, stations_list):
    
    fig = plt.figure(figsize=(20,20))

    resolution = '10m'
    category = 'cultural'
    name = 'admin_0_countries'
    
    shpfilename = shapereader.natural_earth(resolution, category, name)
    df = geopandas.read_file(shpfilename)

    poly2 = df.loc[(df['ADMIN'] == 'Canada')]['geometry'].values[0]
    ax = plt.axes(projection=ccrs.PlateCarree()) 
    ax.add_geometries(poly2, crs=ccrs.PlateCarree(), facecolor='none', edgecolor='0.5')
    ax.stock_img()
    ax.set_extent([-145, -50, 40, 75], crs=ccrs.PlateCarree())
    
    plt.scatter(stations_list.longitude.astype('float'), stations_list.latitude.astype('float'), color='blue', s=0.5)
    if (reqfrom is not None and reqto is not None):
        from_loc = airports_list[airports_list.ident == reqfrom]
        to_loc = airports_list[airports_list.ident == reqto]
        from_long = from_loc['longitude_deg'].iloc[0]
        from_lat = from_loc['latitude_deg'].iloc[0]
        to_long = to_loc['longitude_deg'].iloc[0]
        to_lat = to_loc['latitude_deg'].iloc[0]

        plt.plot([from_long, to_long], [from_lat, to_lat],
            color='red', linestyle='--',
            transform=ccrs.Geodetic(),
        )
    
        plt.plot([from_long, to_long], [from_lat, to_lat],
            color='gray', linestyle='--',
            transform=ccrs.PlateCarree(),
        )

        plt.text(from_long, from_lat, reqfrom,
            horizontalalignment='right', weight='bold', fontsize='x-large',
            transform=ccrs.Geodetic()
        )
    
        plt.text(to_long, to_lat, reqto,
            horizontalalignment='left', weight='bold', fontsize='x-large',
            transform=ccrs.Geodetic()
        )
    
        distance = np.round((geodesic((from_lat, from_long), (to_lat, to_long)).kilometers),2)
        plt.text((from_long + to_long)/2, (from_lat + to_lat)/2, str(distance)+' kms',
            horizontalalignment='left', weight='bold', fontsize='x-large',
            transform=ccrs.Geodetic()
        )
        title = from_loc['name'].iloc[0] + " ---> " + to_loc['name'].iloc[0]   
        plt.title(title)

    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png')
    plt.clf()
    data = base64.b64encode(imgdata.getvalue()).decode()
    return data


def airportcode_autocomplete(request):
    if request.GET.get('q'):
        q = request.GET['q']
        data = Airports.objects.filter(ident__startswith=q).values_list('ident',flat=True)
        json = list(data)
        return JsonResponse(json, safe=False)
    else:
        HttpResponse("No cookies")