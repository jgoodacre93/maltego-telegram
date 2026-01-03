from maltego_trx.transform import DiscoverableTransform
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from settings import app, loop
from extensions import registry
import base64
from dataclasses import dataclass


Smartphone = 'maltego.Smartphone'
DesktopComputer = 'maltego.DesktopComputer'


@dataclass
class DeviceByteMapping:
    hex: str
    os: str
    device: str


def get_device_info_by_image(image_bytes):
    hex_prefix = image_bytes[:100].hex().upper()
    for entry in bytes_os_mapping:
        if hex_prefix.startswith(entry.hex):
            return entry
    return None


bytes_os_mapping = (
    DeviceByteMapping('FFD8FFE000104A46494600010100000100010000FFDB004300090607', 'iOS', Smartphone),
    DeviceByteMapping('FFD8FFE000104A46494600010101004800480000FFE201D84943435F50524F46494C45', 'Android', Smartphone),
    DeviceByteMapping('FFD8FFE000104A464946000101010078', 'Desktop', DesktopComputer),
    DeviceByteMapping('FFD8FFE000104A464946000101010060', 'Desktop, 2', DesktopComputer),
    DeviceByteMapping('FFD8FFE000104A46494600010101004800480000FFE201DB', 'Desktop, 3', DesktopComputer),
    DeviceByteMapping('FFD8FFE000104A46494600010101004800480000FFDB00', 'iOS, Desktop', DesktopComputer),
    DeviceByteMapping('FFD8FFE000104A46494600010101004800480000FFE202', 'Android, old', Smartphone),
    DeviceByteMapping('FFD8FFE000104A4649460001010101', 'Desktop macOS', DesktopComputer),
    DeviceByteMapping('FFD8FFE000104A46494600010101009000900000FFE201DB', 'Desktop macOS, 2', DesktopComputer),
    DeviceByteMapping('FFD8FFE000104A46494600010100000100010000FFDB004300090606', 'macOS', DesktopComputer),
    DeviceByteMapping('FFD8FFE000104A46494600010100000100010000FFDB004300080606', 'macOS, 2', DesktopComputer),
    DeviceByteMapping('FFD8FFE000104A46494600010101009000900000FFDB004300', 'macOS, 3', DesktopComputer),
)


@registry.register_transform(
    display_name="To OS",
    input_entity="interlinked.telegram.CompressedImage",
    description="This Transform identifies the operating system based on the compression byte pattern of the image.",
    output_entities=[Smartphone, DesktopComputer],
)
class CompressedImageToOS(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        image_base64 = request.getProperty("base64")
        image_bytes = base64.b64decode(image_base64)

        device_info = get_device_info_by_image(image_bytes)
        if device_info:
            entity = response.addEntity(device_info.device, value=device_info.os)