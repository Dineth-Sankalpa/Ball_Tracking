from DataFieldTypes import DataFieldTypes

class SubPayloadSchemaas:
    BasicSensorDataSchema = [
            ("TimeStamp", DataFieldTypes.UShort),
            ("Bumper", (DataFieldTypes.Flag1B, [
                ( "Right", 0b00000001),
                ("Center", 0b00000010),
                (  "Left", 0b00000100),
            ])),
            ("WheelDrop", (DataFieldTypes.Flag1B, [
                ("Right", 0b00000001),
                ( "Left", 0b00000010),
            ])),
            ("LeftEncoder", (DataFieldTypes.UShort)),
            ("RightEncoder", (DataFieldTypes.UShort)),
            ("LeftPWM", (DataFieldTypes.SByte)),
            ("RightPWM", (DataFieldTypes.SByte)),
            ("Button", (DataFieldTypes.Flag1B, [
                ("Button0", 0b00000001),
                ("Button1", 0b00000010),
                ("Button2", 0b00000100),
            ])),
            ("Charger", (DataFieldTypes.Flag1B, [
                ("ExternalSupply", 0b00000010),
                ("Charging", 0b00000100),
                ("AdapterConnected", 0b00010000),
            ])),
            ("Battery", (DataFieldTypes.SByte)),
            ("OverCurrent", (DataFieldTypes.Flag1B, [
                ("Right", 0b00000001),
                ( "Left", 0b00000010),
            ])),
        ]

    DockingIRSensorDataSchema = [
        ( "Left", (DataFieldTypes.Flag1B, [
            (  "NearLeft", 0b00000001),
            ("NearCenter", 0b00000010),
            ( "NearRight", 0b00000100),
            (   "FarLeft", 0b00001000),
            ( "FarCenter", 0b00010000),
            (  "FarRight", 0b00100000),
        ])),
        ("Front", (DataFieldTypes.Flag1B, [
            (  "NearLeft", 0b00000001),
            ("NearCenter", 0b00000010),
            ( "NearRight", 0b00000100),
            (   "FarLeft", 0b00001000),
            ( "FarCenter", 0b00010000),
            (  "FarRight", 0b00100000),
        ])),
        ("Right", (DataFieldTypes.Flag1B, [
            (  "NearLeft", 0b00000001),
            ("NearCenter", 0b00000010),
            ( "NearRight", 0b00000100),
            (   "FarLeft", 0b00001000),
            ( "FarCenter", 0b00010000),
            (  "FarRight", 0b00100000),
        ])),
    ]

    InertialSensorDataSchema = [
        ("Angle", (DataFieldTypes.UShort)),
        ("AngleRate", (DataFieldTypes.UShort)),
        ("_", (DataFieldTypes.UByte)),
        ("_", (DataFieldTypes.UByte)),
        ("_", (DataFieldTypes.UByte)),
    ]

    CliffSensorDataSchema = [
        ( "Right", (DataFieldTypes.UShort)),
        ("Center", (DataFieldTypes.UShort)),
        (  "Left", (DataFieldTypes.UShort)),
    ]

    CurrentSensorDataSchema = [ # TODO: Check if this is correct. Current Table in documentation not consistent.
        ("Right", (DataFieldTypes.UShort)),
        ( "Left", (DataFieldTypes.UShort)),
    ]

    HardwareVersionSchema = [
        ("Patch", (DataFieldTypes.UByte)),
        ("Minor", (DataFieldTypes.UByte)),
        ("Major", (DataFieldTypes.UByte)),
        ("_", (DataFieldTypes.UByte)),
    ]

    FirmwareVersionSchema = [
        ("Patch", (DataFieldTypes.UByte)),
        ("Minor", (DataFieldTypes.UByte)),
        ("Major", (DataFieldTypes.UByte)),
        ("_", (DataFieldTypes.UByte)),
    ]

    RawGyroDataSchema = [
    ]

    GPInputDataSchema = [
    ]

    UDIDSchema = [
    ]

    PIDControllerDataSchema = [
    ]