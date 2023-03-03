# This program takes the files from the csv and repackages them as an array of objects

from numpy import cos, sin, deg2rad
from ast import literal_eval
import csv
import sys

import FolderCreator as fc
from Helpers import file2list
import Constants

DISTANCE_BETWEEN_POINTS = Constants.DISTANCE_BETWEEN_POINTS

# Creates Lists of each Data Type from the Paths Given.
latitude_list = file2list(fc.get_latitude_file_path())
longitude_list = file2list(fc.get_longitude_file_path())
height_list = file2list(fc.get_height_file_path())
slope_list = file2list(fc.get_slope_file_path())

# Call from each file instead of class specific calls.
def generate_data_array():
    if not len(longitude_list) == len(latitude_list) == len(height_list) == len(slope_list):
        fc.show_error("ADC App Data Processing Failure", f'Data List Row Lengths are Inconsistent.')
        return

    if not len(longitude_list[0]) == len(latitude_list[0]) == len(height_list[0]) == len(slope_list[0]):
        fc.show_error("ADC App Data Processing Failure", f'Data List Column Lengths are Inconsistent.')
        return

    rows = len(longitude_list)
    cols = len(longitude_list[0])
    xy_dim = len(longitude_list)

    # Change to {fc.archive_path} for final build.
    dataArrayPath = fc.data_path + "/RawDataArray.csv"

    with open(dataArrayPath, mode="w", newline="") as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in range(rows):
            for data_pt in range(cols):
                # dataArray[k][0] = Lat, dA[k][1] = long, dA[k][2] = ht, dA[k][3] = slope
                tmp = [latitude_list[row][data_pt], longitude_list[row][data_pt], height_list[row][data_pt],
                    slope_list[row][data_pt]]
                dataArray.append(tmp)
                csv_writer.writerow(tmp)
    f.close()
    print("Created RawDataArray.csv")

    return xy_dim, dataArrayPath


# Helper Functions for Math
def get_x_coord(lat, long, rad):  # takes in degrees latitude and longitude
    return float(rad) * cos(deg2rad(float(lat))) * cos(deg2rad(float(long)))

def get_y_coord(lat, long, rad):
    return float(rad) * cos(deg2rad(float(lat))) * sin(deg2rad(float(long)))

def get_z_coord(lat, rad):
    return float(rad) * sin(deg2rad(float(lat)))


def write_rect_file(data_arr):
    rect_coord_path = fc.data_path + "/RectangularCoordinateData.csv" # Processed Data Folder given from FolderCreator.py
    xs, ys, zs, = [], [], []
    with open(rect_coord_path, mode="w", newline="") as datafile:
        csv_writer = csv.writer(datafile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range(len(data_arr)):
            lunar_rad = (1737.4 * 1000)  # converts provided lunar rad data to meters
            lat = data_arr[i][0]
            long = data_arr[i][1]
            height = data_arr[i][2]
            slope = float(data_arr[i][3])
            radius = lunar_rad + float(height)

            x = float(get_x_coord(lat, long, radius))/DISTANCE_BETWEEN_POINTS
            y = float(get_y_coord(lat, long, radius))/DISTANCE_BETWEEN_POINTS
            z = float(get_z_coord(lat, radius))/DISTANCE_BETWEEN_POINTS

            csv_writer.writerow([x, y, z, slope])
            xs.append(x), ys.append(y), zs.append(z)
            tmpDataArray.append([x, y, z, slope])

        datafile.close()
    min_x, min_y, min_z = abs(min(xs)), abs(min(ys)), abs(min(zs))
    print("Created RectangularCoordinateData.csv")
    return rect_coord_path, min_x, min_y, min_z


def write_astar_file(xmin, ymin, zmin, tmpArray):
    adjArray = []
    for i in range(len(tmpArray)):
        tmp = [int(tmpArray[i][0]+xmin), int(tmpArray[i][1]+ymin), int(tmpArray[i][2]+zmin), tmpArray[i][3]]
        adjArray.append(tmp)

    sortedArray = sorted(adjArray, key=lambda x: x[1])

    array_to_be_written = []
    for i in range(1277):
        array_to_be_written.append([])

    for i in range(len(sortedArray)):
        array_to_be_written[i // 1277].append(sortedArray[i])

    for i in range(len(array_to_be_written)):
        array_to_be_written[i] = sorted(array_to_be_written[i], key=lambda x: x[0])

    for i in range(len(array_to_be_written)):
        for j in range(len(array_to_be_written[0])):
            array_to_be_written[j][i][0] = i
            array_to_be_written[j][i][1] = j


    # Retrofitted A-Star Data
    astar_path = fc.data_path + "/AStarRawData.csv"
    with open(astar_path, mode="w", newline="") as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in array_to_be_written:
            csv_writer.writerow(row)
    f.close()
    print("Created AStarRawData.csv")

    return astar_path

def test_astar_file():
    astar_path = fc.data_path + "/AStarRawData.csv"
    with open(astar_path, mode="r", newline="") as f:
        astardata = list(csv.reader(f))

    for j in range(len(astardata)):
        for i in range(len(astardata[0])):
            if literal_eval(astardata[j][i])[0] != i:
                if literal_eval(astardata[j][i])[1] != j:
                    print(astardata[j][i])
                    print(i, j)
                    sys.exit(2)


if __name__ == "__main__":
    # Latitude is DataArr[0], Longitude is DataArr[1], Height is DataArr[2], Slope is DataArr[3]
    dataArray = []
    tmpDataArray = []
    x_and_y_dim, data_array_path = generate_data_array()

    rect_file_path, min_x, min_y, min_z, = write_rect_file(dataArray)
    sorted_file_path = write_astar_file(min_x, min_y, min_z, tmpDataArray)
    #test_astar_file()
    print("Data Processing Success")
