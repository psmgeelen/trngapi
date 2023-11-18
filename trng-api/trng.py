import logging
import numpy as np
import subprocess
from pydantic import BaseModel


# Byte Sequence, check what it means
class Handler(object):
    def __init__(self):
        self.logger = logging.getLogger("Handler")
        self.device = self._get_device()

    def get_numbers(self, dtype, n_numbers):
        # When dtype exists, get numbers
        if hasattr(np, dtype):
            self.logger.info(f"Validating the data-type: {dtype}")
            dtype_object = getattr(np, dtype)
            n_bits = self._get_n_bits(dtype_object)
            # Conversion from bits to bytes, 8 bits in one byte
            amount_of_bytes_needed = int(n_bits * n_numbers / 8)
            numbers = self.device.get_random_nrs(
                amount_of_bytes_needed=amount_of_bytes_needed,
                n_numbers=n_numbers,
                dtype=dtype_object,
            )
            actual_length = len(numbers)
        # When dtype doesnt exists, return message
        else:
            self.logger.error(f"Failed to recognize datatype: {dtype}")
            numbers = [
                "Couldn't find dtype: please check out"
                " https://numpy.org/doc/stable/user/basics.types.html for more"
                " information."
            ]
            actual_length = 0

        return randomPayload(
            length=n_numbers,
            actual_length=actual_length,
            dtype=dtype,
            data=numbers,
            device=self.list_devices(),
        )

    def get_hex(self, length):
        hex = self.device.get_random_hex(amount_of_bytes_needed=length)[0:length]

        return randomPayload(
            length=length,
            actual_length=len(hex),
            dtype="bytes",
            data=[hex],
            device=self.list_devices(),
        )

    def list_devices(self):
        return self.device.list_devices()

    def _get_n_bits(self, dtype_object: object) -> int:
        try:
            n_bits = np.finfo(dtype_object).bits
            return n_bits
        except Exception as e:
            self.logger.warning(f"Couldn't detect float: {e}, trying integers now")
            try:
                n_bits = np.iinfo(dtype_object).bits
                return n_bits
            except Exception as e:
                self.logger.error(f"failed to get precision {e}")

    def _get_device(self):
        try:
            p = subprocess.run(["infnoise", "-l"], stdout=subprocess.PIPE)
            if p.returncode == 0:
                self.logger.info(f"Found device(s): {p.stdout}")
                device = Device()
            else:
                self.logger.warning(
                    f"Couldn't find devices, loading emulator. Error: {p.stdout, p.stderr}"
                )
                device = DeviceEmulator()
        except:
            self.logger.warning(
                f"Couldn't find devices, loading emulator"
            )
            device = DeviceEmulator()
        return device


class Device(object):
    def __init__(self):
        self.logger = logging.getLogger("Hardware")

    def get_random_nrs(
        self, amount_of_bytes_needed: int, n_numbers: int, dtype: object
    ) -> list:
        bits = self._get_random_payload(amount_of_bytes_needed=amount_of_bytes_needed)
        return np.frombuffer(buffer=bits[0:amount_of_bytes_needed], dtype=dtype)[
            0:n_numbers
        ].tolist()

    def get_random_hex(self, amount_of_bytes_needed: int) -> bytes:
        bits = self._get_random_payload(amount_of_bytes_needed=amount_of_bytes_needed)
        return bits.hex()

    def _get_random_payload(
        self,
        amount_of_bytes_needed: int,
    ) -> bytearray:
        p = subprocess.Popen("infnoise", stdout=subprocess.PIPE)
        # Get bytes
        bits = bytearray()
        stop = False
        while not stop:
            bits += bytearray(p.stdout.readline(1024))
            if len(bits) > amount_of_bytes_needed:
                stop = True
        return bits

    @staticmethod
    def list_devices():
        p = subprocess.run(["infnoise", "-l"], stdout=subprocess.PIPE)
        return p.stdout


class DeviceEmulator(object):
    def __init__(self):
        self.logger = logging.getLogger("Device Emulator")

    # TODO return bytes
    def get_random_nrs(
        self, amount_of_bytes_needed: int, n_numbers: int, dtype: object
    ) -> list:
        self.logger.info(
            f"Running Emulator, got request for {n_numbers} and"
            f" {amount_of_bytes_needed} amount of bytes"
        )
        return np.random.random(n_numbers).astype(dtype).tolist()

    def get_random_hex(self, amount_of_bytes_needed: int) -> bytes:
        bits = bytearray()
        bits.extend(map(ord, "Hello World"))
        return bits.hex()

    @staticmethod
    def list_devices() -> str:
        return "Emulator"


class dtypeInfo(BaseModel):
    name: str
    dtype_object: object
    n_bits: int


class randomPayload(BaseModel):
    length: int
    actual_length: int
    dtype: str
    data: list
    device: str

    class Config:
        arbitrary_types_allowed = True
