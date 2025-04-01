import datetime, pytz
import matplotlib.pyplot as plt
import numpy as np

import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from glob import glob

import sys
sys.path.append('G:/Мой диск/MyEducation/ИТМО/ВКР/soft')

import vesradcom as vrc
from vesradcom.entities import FiniteLengthDipole, Vessel, Satellite, Landmark, Station
from vesradcom.units import Angle, Frequency, Power, Distance, Velocity


def draw_satellite(ax, sat: Satellite, color, transform):
    ax.plot(sat.subpoint_position().longitude.degrees, sat.subpoint_position().latitude.degrees, 'o', transform=transform, color=color)
    ax.fill(*sat.coverage_area().exterior.xy, transform=transform, facecolor = 'grey', alpha = 0.2, edgecolor='grey')
    ax.plot(*sat.coverage_area().exterior.xy, transform=transform, color=color)
    ax.annotate(sat.title(), (sat.subpoint_position().longitude.degrees - 5, sat.subpoint_position().latitude.degrees + 3), transform=transform, color=color)


def draw_vessel(ax, vessel: Vessel, transform):
    ax.plot(vessel.position().longitude.degrees, vessel.position().latitude.degrees, 'o', color='green', transform=transform)
    ax.annotate("", xytext=(vessel.position().longitude.degrees, vessel.position().latitude.degrees), xy=(vessel.position().longitude.degrees + 10 * np.sin(vessel.course().radians), vessel.position().latitude.degrees + 10 * np.cos(vessel.course().radians)), arrowprops=dict(arrowstyle="->"), transform=transform)


def draw_landmark(ax, landmark: Landmark, transform):
    ax.plot(landmark.position().longitude.degrees, landmark.position().latitude.degrees, 'o', transform=transform, color='blue')
    ax.annotate(landmark.title(), (landmark.position().longitude.degrees - 5, landmark.position().latitude.degrees + 3), transform=transform, color='blue')


def draw_station(ax, station: Station, transform):
    draw_landmark(ax, station, transform)
    ax.plot(*station.coverage_area().exterior.xy, transform=transform, color='blue')


def draw_simulation(ax, sim: vrc.Simulation, track_start_datetime: datetime, track_end_datetime: datetime, transform):
    ax.plot(*sim.area().exterior.xy, '-.', transform=transform, color='green')
    draw_vessel(ax, sim.vessel(), transform)

    draw_parameters(ax, sim.current_datetime(), sim.vessel().position().latitude, sim.vessel().position().longitude,
                    sim.vessel().course(), sim.vessel().velocity(), transform=transform)

    colors = ['red', 'orange', 'blue']
    for i in range(sim.satellite_count()):
        draw_satellite(ax, sim.satellite_at(i), colors[i], transform)
        track = sim.satellite_at(i).track(track_start_datetime, track_end_datetime, datetime.timedelta(minutes=5))
        ax.plot(track.longitude.degrees, track.latitude.degrees, '--', transform=transform, color=colors[i])
        n = len(track.longitude.degrees)
        ax.annotate("", xytext=(track.longitude.degrees[n//2], track.latitude.degrees[n//2]), xy=(track.longitude.degrees[n//2+1], track.latitude.degrees[n//2+1]), arrowprops=dict(facecolor=colors[i], edgecolor=colors[i]), transform=transform)

    for i in range(sim.landmark_count()):
        draw_landmark(ax, sim.landmark_at(i), transform)

    for i in range(sim.station_count()):
        draw_station(ax, sim.station_at(i), transform)


def draw_result_sim(ax, sim: vrc.Simulation, track_start_datetime: datetime,  track_end_datetime: datetime, transform):
    ax.plot(*sim.area().exterior.xy, '-.', transform=transform, color='green')
    draw_vessel(ax, sim.vessel(), transform)

    draw_result(ax, sim.current_datetime(), sim.vessel().position().latitude, sim.vessel().position().longitude,
                    sim.vessel().course(), sim.vessel().velocity(), sim.satellite_at(0).title(), transform=transform)

    for i in range(sim.satellite_count()):
        draw_satellite(ax, sim.satellite_at(i), 'blue', transform)
        track = sim.satellite_at(i).track(track_start_datetime, track_end_datetime, datetime.timedelta(minutes=5))
        ax.plot(track.longitude.degrees, track.latitude.degrees, '--', transform=transform, color='blue')
        n = len(track.longitude.degrees)
        ax.annotate("", xytext=(track.longitude.degrees[n//2], track.latitude.degrees[n//2]), xy=(track.longitude.degrees[n//2+1], track.latitude.degrees[n//2+1]), arrowprops=dict(facecolor='blue', edgecolor='blue'), transform=transform)


def params_to_text(current_datetime: datetime, lat: Angle, lon: Angle, course: Angle, velocity: Velocity) -> str:
    return f'''{current_datetime}\n
Широта: {lat.degrees:.2f}, град\n
Долгота: {lon.degrees:.2f}, град\n
Курс: {course.degrees:.2f}, град\n
Скорость: {velocity.km_per_s * 1000:.2f}, м/с'''


def results_to_text(current_datetime: datetime, lat: Angle, lon: Angle, course: Angle, velocity: Velocity, sat_name: str) -> str:
    return  f'{params_to_text(current_datetime, lat, lon, course, velocity)}\n\nРекомендуемый спутник: {sat_name}'


def draw_parameters(ax, current_datetime: datetime, lat: Angle, lon: Angle, course: Angle, velocity: Velocity, transform):
    ax.text(-175, 30, params_to_text(current_datetime, lat, lon, course, velocity), bbox=dict(ec='black', fc='#E0E0E0'), transform=transform)


def draw_result(ax, current_datetime: datetime, lat: Angle, lon: Angle, course: Angle, velocity: Velocity, sat_name: str, transform):
    ax.text(-175, 25, results_to_text(current_datetime, lat, lon, course, velocity, sat_name), bbox=dict(ec='black', fc='#E0E0E0'), transform=transform)


def main():
    print("Hello!")

    moscow_timezone = pytz.timezone("Europe/Moscow")
    current_datetime = datetime.datetime(2025, 3, 14, 14, 0, 0, tzinfo=moscow_timezone)

    communication_session_start_time = current_datetime + datetime.timedelta(hours=19)
    communication_session_end_time = current_datetime + datetime.timedelta(hours=19.5)

    tle1 = '''EDELVEIS
             1 53385U 22096R   22269.14435733  .00009653  00000-0  37762-3 0  999 5
             2 53385  97.4313 170.3195 0002683 298.0162 199.7004 15.26041929  732 7'''

    tle2 = '''ISS (ZARYA)
    1 25544U 98067A   25074.17888493  .00016842  00000+0  30206-3 0  9990
    2 25544  51.6358  52.6470 0006442  23.0781 337.0496 15.50021799500580'''

    tle3 = '''CSS (TIANHE)
    1 48274U 21035A   25073.70705526  .00024039  00000+0  27594-3 0  9992
    2 48274  41.4641 235.9815 0006472 344.7039  15.3603 15.61470209221388'''
    
    antenna = FiniteLengthDipole(Frequency(hz=1e+6), Power(w=3.7e-12), Power(w=12), Power(w=10))
    vessel = Vessel(Angle(degrees=-10), Angle(degrees=-15), Angle(degrees=20), Velocity(km_per_s=0.02))
    area = [(-73, 40), (-10, 40), (-18, 22), (-18, 12), (-8, 2.6), (8, 2.6), (8, -35), (-49, -35), (-32, -6), (-76, 31)]

    simulation = vrc.Simulation(area = area, antenna = antenna, vessel = vessel)

    simulation.append_satellite(Satellite(tle1, Power(0.4), 1))
    simulation.append_satellite(Satellite(tle2, Power(0.4), 1)) 
    simulation.append_satellite(Satellite(tle3, Power(0.4), 1))
    simulation.set_current_datetime(current_datetime)
    simulation.update()

    for i in range(simulation.satellite_count()):
        print(f'satellite {i} visible:', simulation.satellite_at(i).visible())
        print(f'satellite {i} detectable:', simulation.satellite_at(i).detectable())

    results = simulation.bruteforce(communication_session_start_time, communication_session_end_time)

    res_sim = vrc.Simulation()

    if results:
        print(results[0])
        res_sim = vrc.from_bruteforce_result(simulation, results[0])

    # projection = ccrs.AzimuthalEquidistant(central_latitude=simulation.vessel().position().latitude.degrees, central_longitude=simulation.vessel().position().longitude.degrees)
    projection = ccrs.PlateCarree()
    transform = ccrs.Geodetic()

    fig1 = plt.figure(figsize=(15, 7))
    ax1 = fig1.add_subplot(1, 1, 1, projection=projection)
    fig2 = plt.figure(figsize=(15, 7))
    ax2 = fig2.add_subplot(1, 1, 1, projection=projection)

    shape_files_dir_path = 'G:/Мой диск/MyEducation/ИТМО/ВКР/soft/python/first_steps/10m_physical'
    shape_files = glob(shape_files_dir_path + '/ne_10m_land.shp')
    for shape_file in shape_files:
        shape_feature = ShapelyFeature(Reader(shape_file).geometries(), ccrs.PlateCarree(), facecolor='none', alpha = 0.5)
        ax1.add_feature(shape_feature)
        ax2.add_feature(shape_feature)

    ax1.set_global()
    ax2.set_global()
    
    draw_simulation(ax1, simulation, communication_session_start_time, communication_session_end_time, transform=transform)
    
    if results:
        draw_result_sim(ax2, res_sim, communication_session_start_time, communication_session_end_time, transform=transform)
    
    plt.show()

if __name__ == "__main__":
    main()