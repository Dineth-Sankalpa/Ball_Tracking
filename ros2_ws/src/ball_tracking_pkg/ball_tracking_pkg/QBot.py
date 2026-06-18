import serial


class SubPayloadDecoders:
    def BasicSensorDataDecoder(subPayload):
        pass

    def DockingIRSensorDataDecoder(subPayload):
        pass

    def InertialSensorDataDecoder(subPayload):
        pass

    def CliffSensorDataDecoder(subPayload):
        pass

    def CurrentSensorDataDecoder(subPayload):
        pass

    def HardwareVersionDecoder(subPayload):
        pass

    def FirmwareVersionDecoder(subPayload):
        pass

    def RawGyroDataDecoder(subPayload):
        pass

    def GPInputDataDecoder(subPayload):
        pass

    def UDIDDecoder(subPayload):
        pass

    def PIDControllerDataDecoder(subPayload):
        pass

class QBot:
    def __init__(self, serialPort):
        self.serial = serial.Serial(
            port = serialPort,
            baudrate = 115200,
        )

        self.sensorData = {}

    def divideToSubPayloads(self, payload):
        subPayloads = {}
        index = 0
        while index < len(payload):
            subPayloadLength = payload[index+1]
            subPayloads[bytes([payload[index]])] = payload[index:index+subPayloadLength+2]
            index += subPayloadLength+2
        return subPayloads

    def readPayload(self):
        payloadReceived = False
        while not payloadReceived:
            while self.serial.read() != b'\xAA': # TODO: Checkk if this is randomly a byte sequence in the data
                pass # TODO: set a timeout
            if self.serial.read() == b'\x55':
                payloadReceived = True
                payloadLength = self.serial.read()[0]
                payload = self.serial.read(payloadLength)
                checksum = self.serial.read()
                return payload if self.calculateChecksum(payload) == checksum else None

    def calculateChecksum(self, payload):
        checksum = len(payload)
        for byte in payload:
            checksum = byte ^ checksum
        return bytes([checksum])

    def set_velocity(self, speed, radius):
        """
        Sends a Base Control payload to move the Kobuki base.
        :param speed: Speed in mm/s
        :param radius: Radius in mm. 0 = straight, 1 = turn in place CCW, -1 = turn in place CW
        """
        # Payload: ID 0x01 (Base Control), Length 4 bytes
        payload = bytearray([0x01, 0x04]) 
        
        # Add Speed (2 bytes, little-endian, signed)
        payload.extend(int(speed).to_bytes(2, byteorder='little', signed=True))
        
        # Add Radius (2 bytes, little-endian, signed)
        payload.extend(int(radius).to_bytes(2, byteorder='little', signed=True))
        
        # Calculate checksum and build final packet
        checksum = self.calculateChecksum(payload)
        packet = bytearray([0xAA, 0x55, len(payload)]) + payload + checksum
        
        # Send to robot
        self.serial.write(packet)
    
    def decodeSubPayload(self, ):
    	pass
    


    def close(self):
        self.serial.close()

   
    subPayloadDecoders = {
        b'\x01': SubPayloadDecoders.BasicSensorDataDecoder,
        b'\x03': SubPayloadDecoders.DockingIRSensorDataDecoder,
        b'\x04': SubPayloadDecoders.InertialSensorDataDecoder,
        b'\x05': SubPayloadDecoders.CliffSensorDataDecoder,
        b'\x06': SubPayloadDecoders.CurrentSensorDataDecoder,
        b'\x0A': SubPayloadDecoders.HardwareVersionDecoder,
        b'\x0B': SubPayloadDecoders.FirmwareVersionDecoder,
        b'\x0D': SubPayloadDecoders.RawGyroDataDecoder,
        b'\x10': SubPayloadDecoders.GPInputDataDecoder,
        b'\x13': SubPayloadDecoders.UDIDDecoder,
        b'\x15': SubPayloadDecoders.PIDControllerDataDecoder
    }
