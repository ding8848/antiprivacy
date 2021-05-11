import exifread
import re
import json
import requests
import os

# change the mode of latitude and longitude
def latitude_and_longitude_convert_to_decimal_system(*arg):
    """
    transform latitude and longitude to decimal
    """
    return float(arg[0]) + ((float(arg[1]) + (float(arg[2].split('/')[0]) / float(arg[2].split('/')[-1]) / 60))/60)

# read GPS from picture
def find_GPS_image(pic_path):
    GPS = {}
    date = ''
    with open(pic_path, 'rb') as f:
        tags = exifread.process_file(f)
        for tag, value in tags.item():
            # latitude
            if re.match('GPS GPSLatitudeRef', tag):
                GPS['GPSLatitudeRef'] = str(value)
            # longitude
            elif re.match('GPS GPSLongitudeRef', tag):
                GPS['GPSLongitudeRef'] = str(value)
            # altitude
            elif re.match('GPS GPSAltitudeRef', tag):
                GPS['GPSAltitudeRef'] = str(value)
            elif re.match('GPS GPSLatitude', tag):
                try:
                    match_result = re.match('\[(\w*),(\w*),(\w.*)/(\w.*)\]',str(value)).groups()
                    GPS['GPSLatitude'] = int(match_result[0]),int(match_result[1]),int(match_result[2])
                except:
                    deg, min, sec = [x.replace(' ','') for x in str(value)[1:-1].split(',')]
                    GPS['GPSLatitude'] = latitude_and_longitude_convert_to_decimal_system(deg,min,sec)
            elif re.match('GPS GPSLongitude', tag):
                try:
                    match_result = re.match('\[(\w*),(\w*),(\w.*)/(\w.*)\]',str(value)).groups()
                    GPS['GPSLongitude'] = int(match_result[0]),int(match_result[1]),int(match_result[2])
                except:
                    deg, min, sec = [x.replace(' ','') for x in str(value)[1:-1].split(',')]
                    GPS['GPSLongitude'] = latitude_and_longitude_convert_to_decimal_system(deg,min,sec)
            elif re.match('GPS GPSAltitude', tag):
                GPS['GPSAltitude'] = str(value)
            elif re.match('.*Date.*', tag):
                date = str(value)

            return {'GPS_information':GPS, 'date_information':date}

# use baidu Map API to convert the GPS message into address
def find_address_from_GPS(GPS):
    # you need to input your api_key here
    secret_key = ''
    if not GPS['GPS_infomation']:
        return 'The information of this picture is empty.'
    lat,lng = GPS['GPS_information']['GPSLatitude'],GPS['GPS_information']['GPSLongitude']
    # you need to input your api url here
    baidu_map_api = "".format(secret_key, lat, lng)
    response = requests.get(baidu_map_api)
    content = response.text.replace("renderReverse&&renderReverse(", "")[:-1]
    print(content)
    baidu_map_address = json.loads(content)
    formatted_address = baidu_map_address["result"]["formatted_address"]
    province = baidu_map_address["result"]["addressComponent"]["province"]
    city = baidu_map_address["result"]["addressComponent"]["city"]
    district = baidu_map_address["result"]["addressComponent"]["district"]
    location = baidu_map_address["result"]["sematic_description"]
    return formatted_address,province,city,district,location
if __name__ == '__main__':
    pic_path = input()
    GPS_info = find_GPS_image(pic_path)
    address = find_address_from_GPS(GPS=GPS_info)
    print("拍摄时间：" + GPS_info.get("date_information"))
    print('照片拍摄地址:' + str(address))