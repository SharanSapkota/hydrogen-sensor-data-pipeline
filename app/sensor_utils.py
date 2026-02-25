TOTAL_NUMBER_OF_SENSORS = 10

def meanValueOfAllSensors(sensor_buffer):
    if len(sensor_buffer) == 0:
        return 0

    mean = sum(sensor_buffer.values()) / len(sensor_buffer)

    return mean

def build_sensor_value_vector(sensor_buffer):
    sensor_vector = []
    if len(sensor_buffer) == 0:
        return None
    
    for sensorId in range(1, TOTAL_NUMBER_OF_SENSORS + 1):
        if sensorId in sensor_buffer:
            sensorValue = sensor_buffer[sensorId]
        else:
            sensorValue = meanValueOfAllSensors(sensor_buffer)
        sensor_vector.append(sensorValue)

    return sensor_vector
