#!/usr/bin/env python
from modulos import auxiliar as auxiliar
class lcd:
  
   """
   Commands

   LCD_CLEARDISPLAY = 0x01
   LCD_RETURNHOME = 0x02
   LCD_ENTRYMODESET = 0x04
   LCD_DISPLAYCONTROL = 0x08
   LCD_CURSORSHIFT = 0x10
   LCD_FUNCTIONSET = 0x20
   LCD_SETCGRAMADDR = 0x40
   LCD_SETDDRAMADDR = 0x80

   Flags for display entry mode

   LCD_ENTRYRIGHT = 0x00
   LCD_ENTRYLEFT = 0x02
   LCD_ENTRYSHIFTINCREMENT = 0x01
   LCD_ENTRYSHIFTDECREMENT = 0x00

   Flags for display on/off control

   LCD_DISPLAYON = 0x04
   LCD_DISPLAYOFF = 0x00
   LCD_CURSORON = 0x02
   LCD_CURSOROFF = 0x00
   LCD_BLINKON = 0x01
   LCD_BLINKOFF = 0x00

   Flags for display/cursor shift

   LCD_DISPLAYMOVE = 0x08
   LCD_CURSORMOVE = 0x00
   LCD_MOVERIGHT = 0x04
   LCD_MOVELEFT = 0x00

   Flags for function set

   LCD_8BITMODE = 0x10
   LCD_4BITMODE = 0x00
   LCD_2LINE = 0x08
   LCD_1LINE = 0x00
   LCD_5x10DOTS = 0x04
   LCD_5x8DOTS = 0x00

   Flags for backlight control

   LCD_BACKLIGHT = 0x08
   LCD_NOBACKLIGHT = 0x00
   """

   _LCD_ROW = [0x80, 0xC0, 0x94, 0xD4]

   def __init__(self, pi, bus=1, addr=0x27, width=16, backlight_on=True,
                RS=0, RW=1, E=2, BL=3, B4=4):
                
      auxiliar.EscribirFuncion("lcd - __init__")

      self.pi = pi
      self.width = width
      self.backlight_on = backlight_on

      self.RS = (1<<RS)
      self.E  = (1<<E)
      self.BL = (1<<BL)
      self.B4 = B4

      self._h = pi.i2c_open(bus, addr)

      self._init()

   def backlight(self, on):
      auxiliar.EscribirFuncion("lcd - backlight")

      """
      Switch backlight on (True) or off (False).
      """
      self.backlight_on = on

   def _init(self):
      auxiliar.EscribirFuncion("lcd - _init")

      self._inst(0x33) # Initialise 1
      self._inst(0x32) # Initialise 2
      self._inst(0x06) # Cursor increment
      self._inst(0x0C) # Display on,move_to off, blink off 
      self._inst(0x28) # 4-bits, 1 line, 5x8 font
      self._inst(0x01) # Clear display

   def _byte(self, MSb, LSb):
      auxiliar.EscribirFuncion("lcd - _byte")

      if self.backlight_on:
         MSb |= self.BL
         LSb |= self.BL

      self.pi.i2c_write_device(self._h,
         [MSb | self.E, MSb & ~self.E, LSb | self.E, LSb & ~self.E])

   def _inst(self, bits):
      auxiliar.EscribirFuncion("lcd - _inst")

      MSN = (bits>>4) & 0x0F
      LSN = bits & 0x0F

      MSb = MSN << self.B4
      LSb = LSN << self.B4

      self._byte(MSb, LSb)

   def _data(self, bits):
      auxiliar.EscribirFuncion("lcd - _data")

      MSN = (bits>>4) & 0x0F
      LSN = bits & 0x0F

      MSb = (MSN << self.B4) | self.RS
      LSb = (LSN << self.B4) | self.RS

      self._byte(MSb, LSb)

   def move_to(self, row, column):
      auxiliar.EscribirFuncion("lcd - move_to")

      """
      Position cursor at row and column (0 based).
      """
      self._inst(self._LCD_ROW[row]+column)

   def put_inst(self, byte):
      auxiliar.EscribirFuncion("lcd - put_inst")

      """
      Write an instruction byte.
      """
      self._inst(byte)

   def put_symbol(self, index):
      auxiliar.EscribirFuncion("lcd - put_symbol")

      """
      Write the symbol with index at the current cursor postion
      and increment the cursor.
      """
      self._data(index)

   def put_chr(self, char):
      auxiliar.EscribirFuncion("lcd - put_chr")

      """
      Write a character at the current cursor postion and
      increment the cursor.
      """
      self._data(ord(char))

   def put_str(self, text):
      auxiliar.EscribirFuncion("lcd - put_str")

      """
      Write a string at the current cursor postion.  The cursor will
      end up at the character after the end of the string.
      """
      for i in text:
         self.put_chr(i)

   def put_line(self, row, text):
      auxiliar.EscribirFuncion("lcd - put_line")

      """
      Replace a row (0 based) of the LCD with a new string.
      """
      text = text.ljust(self.width)[:self.width]

      self.move_to(row, 0)

      self.put_str(text)

   def close(self):
      auxiliar.EscribirFuncion("lcd - close")
      
      """
      Close the LCD (clearing the screen) and release used resources.
      """
      self._inst(0x01)

      self.pi.i2c_close(self._h)

