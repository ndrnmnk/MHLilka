#/*
# * ----------------------------------------------------------------------------
# * "THE BEER-WARE LICENSE" (Revision 42 modified):
# * <maple@maple.pet> wrote this file.  As long as you retain this notice and
# * my credit somewhere you can do whatever you want with this stuff.  If we
# * meet some day, and you think this stuff is worth it, you can buy me a beer
# * in return.
# * ----------------------------------------------------------------------------
# */

## !!!
## this lib NEEDS micropython 1.23.0 or above!
## see https://github.com/micropython/micropython/pull/13727
## !!!

"""
Library for I2S software sound mixing developed primarily for the M5 Cardputer.

https://maple.pet/
"""

import array
import time

from machine import I2S, Pin


_PERIODS = [ # c-0 thru b-0 - how much to advance a sample pointer per frame for each note
	b'\x01\x00\x00\x00\x00\x00\x00\x00',
	b'\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00',
	b'\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00',
	b'\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00',
	b'\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00',
	b'\x01\x00\x00\x00\x00\x00',
	b'\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00',
	b'\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00',
	b'\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00',
	b'\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00',
	b'\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00',
	b'\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00',
]

_INT_MINVAL = const(-32768)
_INT_MAXVAL = const(32767)

_MH_I2S_SCK = const(42)
_MH_I2S_WS = const(1)
_MH_I2S_SD = const(2)

# Enable the amplifier
amp_sd = Pin(46, Pin.OUT)
amp_sd.value(1)  # drive high to enable amp

@micropython.viper
def _volume(volume:int) -> int:
	"""Convert volume to bit shift.

	Returns volume 0-30 reversed in order to be used in bitshifting.
	15 is 100% (no bitshift)
	"""
	if volume <= 0:
		return 15
	if volume <= 30:
		return 15 - volume
	return -15

@micropython.viper
def _vipmod(a:int, b:int) -> int:
	"""Quick viper-friendly modulo."""
	while a >= b:
		a -= b
	return a

# streaming samples from sd card without using much ram oh yeah i'm feeling really clever!!
class Sample:
	"""Store a sample from a memoryview or file."""

	def __init__(self, source, buffer_size=1024):
		"""Initialize a sample for playback.

		- source: If string, filename. Otherwise, use MemoryView.
		- buffer_size: If loading from filename, the size to buffer in RAM.
		"""
		if type(source) is str:
			from os import stat
			self.length = stat(source)[6]
			if self.length < buffer_size:
				buffer_size = self.length
			self.buffer = bytearray(buffer_size)
			self.buf_mv = memoryview(self.buffer)
			self.file = open(source, "rb")  # noqa: SIM115
			self.start = 0
			self.end = self.file.readinto(self.buf_mv)
		elif type(source) is memoryview:
			self.file = None
			self.buf_mv = source
			self.start = 0
			self.end = len(source)
			self.length = len(source)
		else:
			raise TypeError

	def __len__(self):
		return self.length

	def load(self, ptr):
		"""Load data from file into buffer."""
		if self.file:
			self.start = ptr
			self.file.seek(self.start)
			read = self.file.readinto(self.buf_mv)
			self.end = self.start + read

	# not sure this ever worked or if i want to go this route
	#def __getitem__(self, key):
	#	if type(key) != int:
	#		raise TypeError
	#	if self.file:
	#		if key < self.start or key >= self.end:
	#			self.start = key
	#			self.file.seek(self.start)
	#			read = self.file.readinto(self.buf_mv)
	#			self.end = self.start + read
	#	return self.buf_mv[key - self.start:]

	def __del__(self):
		if self.file:
			self.file.close()
			del(self.buffer)

class Register:
	"""Stores settings for timed playback of samples in I2SSound."""

	def __init__(
			self,
			*,
			buf_start=0,
			sample=None,
			pointer=0,
			note=0,
			period=1,
			period_mult=4,
			loop=False,
			volume=0):
		"""Create a new Register."""
		self.buf_start = buf_start
		self.sample = sample
		self.pointer = pointer
		self.period = period
		self.note = note
		self.period_mult = period_mult
		self.loop = loop
		self.volume = volume

	def copy(self) -> 'Register':
		"""Clone this Register."""
		registers = Register()
		registers.buf_start = self.buf_start
		registers.sample = self.sample
		registers.pointer = self.pointer
		registers.period = self.period
		registers.note = self.note
		registers.period_mult = self.period_mult
		registers.loop = self.loop
		registers.volume = self.volume
		return registers

	def __str__(self):
		return f"{self.buf_start}: {self.sample} v:{self.volume} n:{self.note}"

class I2SSound:
	"""The main driver class for playing sound from an I2S speaker."""

	def __init__(
			self,
			buf_size=2048,
			rate=11025,
			channels=4,
			sck=_MH_I2S_SCK,
			ws=_MH_I2S_WS,
			sd=_MH_I2S_SD):
		"""Initialize I2S using the given values."""
		self._output = I2S(
			1,
			sck=Pin(sck),
			ws=Pin(ws),
			sd=Pin(sd),
			mode=I2S.TX,
			bits=16,
			format=I2S.MONO,
			rate=rate,
			ibuf=buf_size,
		)

		self._rate = rate
		self._buf_size:int = buf_size
		self._buffer = array.array('h', range(buf_size))
		self._buf_mv = memoryview(self._buffer)
		self.channels = channels
		self._registers = [Register() for _ in range(channels)]
		self._queues = [[] for _ in range(channels)]
		self._last_tick = 0
		self._output.irq(self._process_buffer)
		self._process_buffer(None)

	def __del__(self):
		self._output.deinit()

	@micropython.native
	def _gen_buf_start(self) -> int:
		return int(time.ticks_diff(time.ticks_us(), self._last_tick) // (1000000 / self._rate))

	@micropython.native
	def play(
		self,
		sample,
		*,
		note=0,
		octave=4,
		volume=15,
		channel=0,
		loop=False):
		"""Schedules a sample to be played immediately.

		- sample:
			Sample or MemoryView for a sample.
			Must be 16bits mono, sample rate matching M5Sound constructor.
		- note:
			Numerical 0-12 mapping from C-0 to B-0.
			Numbers outside that range will affect octave as well.
		- octave:
			Octave to play the sample at.
			By default C-4 which corresponds to unalterated sample.
		- volume:
			Volume the sample should play at, range 0-15.
		- channel:
			Channel the sample should play on,
			must be within range of channels defined in M5Sound constructor.
		- loop:
			If True, sample will loop forever until channel is stopped.
		"""
		if type(sample) is bytearray or type(sample) is bytes:
			source = Sample(memoryview(sample))
		elif type(sample) is memoryview:
			source = Sample(sample)
		elif type(sample) is Sample:
			source = sample
		else:
			raise TypeError

		registers = Register(
			buf_start = self._gen_buf_start(),
			sample = source,
			loop = loop,
			note = note % 12,
			period_mult = 2 ** ((octave-1 if octave > 0 else 0) + (note // 12)),
			volume = volume,
		)
		self._queues[channel].append(registers)

	@micropython.native
	def stop(self, channel=0):
		"""Schedules a channel to stop playing immediately."""
		registers = Register(buf_start=self._gen_buf_start())  # default has empty sample
		self._queues[channel].append(registers)

	@micropython.native
	def setvolume(self, volume, channel=0):
		"""Set the volume of a channel immediately, preserving sample already being played there."""
		if len(self._queues[channel]) > 0:
			registers = self._queues[channel][-1].copy()
		else:
			registers = self._registers[channel].copy()
		registers.buf_start = self._gen_buf_start()
		registers.volume = volume
		self._queues[channel].append(registers)

	@micropython.viper
	def _clear_buffer(self):
		"""Zero out internal buffer."""
		buf = ptr16(self._buf_mv)
		for i in range(int(self._buf_size)):
			buf[i] = 0

	@micropython.viper
	def _fill_buffer(self, registers, end:int):
		"""Take a sample register and fill internal buffer with it."""
		buf = ptr16(self._buf_mv)
		start = int(registers.buf_start)
		ptr = int(registers.pointer)
		smp = ptr16(registers.sample.buf_mv)
		slen = int(len(registers.sample))>>1
		sbstart = int(registers.sample.start)>>1
		sbend = int(registers.sample.end)>>1
		per = ptr8(_PERIODS[registers.note])
		perlen = int(len(_PERIODS[registers.note]))
		perptr = int(registers.period)
		permult = int(registers.period_mult)
		vol = int(_volume(registers.volume))
		loop = bool(registers.loop)
		for i in range(start, end):
			if ptr >= slen: # sample ended
				if not loop: # stop playing
					registers.sample = None
					return
				ptr = int(_vipmod(ptr, slen)) # or loop
			if ptr < sbstart or ptr >= sbend:
				# sample buffer end, load more from sdcard
				# we're doing funny shifts because ptr is 16bit word and outside uses single bytes
				registers.sample.load(ptr<<1)
				sbstart = int(registers.sample.start)>>1
				sbend = int(registers.sample.end)>>1
			bsmp = int(smp[ptr-sbstart])
			bsmp_int = (int(smp[ptr-sbstart]) - 0b10000000000000000) if bsmp & 0b1000000000000000 else bsmp
			buf_int = (int(buf[i]) - 0b10000000000000000) if buf[i] & 0b1000000000000000 else buf[i]
			if vol < 0:
				bsmp_int <<= (0-vol)
			else:
				bsmp_int >>= vol
			res = bsmp_int + buf_int
			buf[i] = (
				_INT_MINVAL if res < _INT_MINVAL
				else _INT_MAXVAL if res > _INT_MAXVAL
				else res
			)
			if res < 0:
				buf[i] |= 0b1000000000000000
			for _ in range(permult): # add together frame periods for different octaves
				ptr += per[perptr]
				perptr += 1
				if perptr >= perlen:
					perptr = 0
		registers.buf_start = 0
		registers.pointer = ptr
		registers.period = perptr

	@micropython.native
	def _process_buffer(self, arg):  # noqa: ARG002 # `arg` required for IRQ callback
		"""I2S IRQ function to process register queue."""
		self._output.write(self._buf_mv)
		self._clear_buffer()
		self._last_tick = time.ticks_us()

		for ch in range(int(self.channels)):
			playing = True
			while playing:
				registers = self._registers[ch]

				end = self._buf_size
				if len(self._queues[ch]) > 0 and self._queues[ch][0].buf_start < self._buf_size:
					end = self._queues[ch][0].buf_start
					self._registers[ch] = self._queues[ch].pop(0)
				else:
					playing = False

				if registers.sample:
					self._fill_buffer(registers, end)

		for ch in range(int(self.channels)):
			if self._registers[ch].sample:
				self._registers[ch].sample.load(self._registers[ch].pointer<<1)
			for reg in self._queues[ch]:
				if reg.buf_start >= self._buf_size:
					reg.buf_start -= self._buf_size
