import time
from QBot import QBot

# Replace with the port you found in Step 1
SERIAL_PORT = '/dev/ttyUSB0' 

def main():
    print(f"Attempting to connect to Kobuki on {SERIAL_PORT}...")
    
    try:
        # Initialize the robot connection
        # The QBot class automatically sets the baudrate to 115200
        robot = QBot(SERIAL_PORT)
        print("Serial port opened successfully!")

        print("Listening for incoming data payloads...")
        # Attempt to read one valid payload from the robot
        payload = robot.readPayload() 
        
        if payload:
            print("Success! Received a valid payload from the Kobuki base.")
            print(f"Payload length: {len(payload)} bytes")
            # The divideToSubPayloads method can be used to split this raw data
            sub_payloads = robot.divideToSubPayloads(payload)
            print(f"Found {len(sub_payloads)} sub-payloads inside the packet.")
        else:
            print("Failed. Received data, but checksum was invalid.")

    except Exception as e:
        print(f"Connection failed: {e}")
        
    finally:
        # Always close the serial port safely
        if 'robot' in locals():
            robot.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()
