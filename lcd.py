from machine import Pin, SPI, PWM
import framebuf
import time

# --- Pinos padrão Waveshare RP2350 LCD 1.47" ---
BL = 21
DC = 16
RST = 20
MOSI = 19
SCK = 18
CS = 17

class LCD_1inch47(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 320
        self.height = 172
        
        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)
        self.dc = Pin(DC, Pin.OUT)
        self.cs(1)
        self.dc(1)

        # Inicializar SPI0 (sem MISO)
        self.spi = SPI(0, baudrate=100_000_000, polarity=0, phase=0,
                       sck=Pin(SCK), mosi=Pin(MOSI), miso=None)

        # Framebuffer em RGB565
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

        # --- Paleta de cores correta (RGB real) ---
        self.BLACK   = 0x0000
        self.WHITE   = 0xFFFF
        self.RED     = 0x07E0   # trocar R <-> G
        self.GREEN   = 0x001F # trocar R <-> G
        self.BLUE    = 0xF800
        self.MAGENTA = 0xFFE0
        self.YELLOW = 0x07FF
        self.CYAN  = 0xF81F


    # --- Comunicação SPI ---
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, data):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        if isinstance(data, int):
            data = bytearray([data])
        self.spi.write(data)
        self.cs(1)

    # --- Inicialização do controlador ST7789 (modo BGR) ---
    def init_display(self):
        self.rst(1)
        self.rst(0)
        self.rst(1)

        self.write_cmd(0x36)
        self.write_data(0x70)  # BGR order (CORRETO para este painel)

        self.write_cmd(0x3A)
        self.write_data(0x05)

        self.write_cmd(0xB2)
        for d in [0x0C, 0x0C, 0x00, 0x33, 0x33]:
            self.write_data(d)

        for cmd, data in [
            (0xB7, [0x35]),
            (0xC0, [0x2C]),
            (0xC2, [0x01]),
            (0xC3, [0x13]),
            (0xC4, [0x20]),
            (0xC6, [0x0F]),
            (0xD0, [0xA4, 0xA1]),
        ]:
            self.write_cmd(cmd)
            for d in data:
                self.write_data(d)

        self.write_cmd(0x21)  # Inversão
        self.write_cmd(0x11)  # Sleep out
        self.write_cmd(0x29)  # Display on

    # --- Enviar framebuffer completo ---
    def show(self):
        self.write_cmd(0x2A)
        for d in [0x00, 0x00, 0x01, 0x3F]:
            self.write_data(d)

        self.write_cmd(0x2B)
        for d in [0x00, 0x22, 0x00, 0xCD]:
            self.write_data(d)

        self.write_cmd(0x2C)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

    # --- Texto escalável (mesmo que versão original) ---
    def write_text(self, text, x, y, size, color):
        background = self.pixel(x, y)
        info = []
        self.text(text, x, y, color)
        for i in range(x, x + (8 * len(text))):
            for j in range(y, y + 8):
                if self.pixel(i, j) == color:
                    info.append((i, j, color))
        self.text(text, x, y, background)
        for px_info in info:
            self.fill_rect(size * px_info[0] - (size - 1) * x,
                           size * px_info[1] - (size - 1) * y,
                           size, size, px_info[2])