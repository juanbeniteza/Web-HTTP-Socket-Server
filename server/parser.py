WeatherObject = {
  'summary': None,
  'forecastMessage': None,
  'temperature': None,
  'address': None,
  'iconito': None,
  'timezone': None,
  'imageURL': None,
}


def parser(data):

    WeatherObject['summary'] = data['currently']['summary']
    WeatherObject['temperature'] = int(data['currently']['temperature'])
    WeatherObject['forecastMessage'] = data['daily']['summary']
    WeatherObject['timezone'] = data['timezone']
    WeatherObject['address'] = data['address']
    WeatherObject['iconito'] = data['currently']['icon']
    
    return WeatherObject