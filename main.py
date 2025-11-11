"""
Display Emby LCARS - Modo Híbrido
---------------------------------
Autor: Ama
Versão: 2.0 (híbrida)
Descrição:
    - Mostra arranque animado LCARS com efeito fluorescente.
    - Entra em modo ativo, atualizando dados recebidos via USB.
    - Se não receber dados, mostra 'N/A' em cada campo.
    - Compatível com Linux:
        echo "Server: Emby|IP: 192.168.1.100|Status: Online" > /dev/ttyACM0
"""

from machine import PWM, Pin
from lcd import LCD_1inch47
import time, math, random, sys

# ---------------------------------------------------------------
#  INICIALIZAÇÃO
# ---------------------------------------------------------------
lcd = LCD_1inch47()
lcd.fill(lcd.BLACK)
bar_h = 25

# Backlight control
bl = PWM(Pin(21))
bl.freq(1000)

# --- Ajuste automático de brilho conforme hora local ---
try:
    import time
    hour = time.localtime()[3]
    if 21 <= hour or hour < 7:
        bl.duty_u16(7000)   # modo noturno (~25% brilho)
    else:
        bl.duty_u16(30000)   # modo normal (~55% brilho)
except Exception:
    bl.duty_u16(7000)       # fallback se o tempo não estiver disponível


# ---------------------------------------------------------------
#  FUNÇÕES DE ILUMINAÇÃO
# ---------------------------------------------------------------

def backlight_flicker():
    """Efeito lâmpada fluorescente a acender (início)."""
    bl.duty_u16(0)
    for _ in range(random.randint(4, 7)):
        duty = random.randint(15000, 40000)
        bl.duty_u16(duty)
        time.sleep(random.uniform(0.01, 0.15))
        bl.duty_u16(0)
        time.sleep(random.uniform(0.01, 0.15))
    for d in range(0, 65535, 3000):
        bl.duty_u16(d)
        time.sleep(0.02)
    bl.duty_u16(65535)

def backlight_flicker_soft():
    """Piscar suave - pequenas variações de brilho."""
    for _ in range(2):
        bl.duty_u16(random.randint(1000, 60000))
        time.sleep(0.1)
        bl.duty_u16(65535)
        time.sleep(0.1)

# ---------------------------------------------------------------
#  FUNÇÕES DE DESENHO LCARS
# ---------------------------------------------------------------

def draw_header(title="EMBY"):
    """Cabeçalho LCARS com cantos convexos e título centrado."""
    lcd.fill_rect(0, 0, 320, bar_h, lcd.YELLOW)
    for y in range(bar_h):
        dx = int(math.sqrt(bar_h**2 - (bar_h - y)**2))
        for x in range(0, bar_h - dx):
            lcd.pixel(x, y, lcd.BLACK)
        for x in range(320 - (bar_h - dx), 320):
            lcd.pixel(x, y, lcd.BLACK)
    size = 3
    text_width = len(title) * 8 * size
    x_center = (320 - text_width) // 2
    lcd.write_text(title, x_center, 2, size, lcd.BLACK)
    lcd.show()

def animate_header():
    """Animação de arranque LCARS."""
    for w in range(0, 321, 4):
        lcd.fill(lcd.BLACK)
        lcd.fill_rect(0, 0, w, bar_h, lcd.YELLOW)
        for y in range(bar_h):
            dx = int(math.sqrt(bar_h**2 - (bar_h - y)**2))
            for x in range(0, bar_h - dx):
                lcd.pixel(x, y, lcd.BLACK)
            for x in range(320 - (bar_h - dx), 320):
                lcd.pixel(x, y, lcd.BLACK)
        lcd.show()
        time.sleep(0.0005)

def draw_bottom_bars():
    """Desenha quatro barras coloridas na parte inferior."""
    bar_w, bar_h2, gap, y_pos = 60, 10, 10, 140
    colors = [lcd.BLUE, lcd.CYAN, lcd.GREEN, lcd.YELLOW]
    total_w = (bar_w * 4) + (gap * 3)
    x_start = (320 - total_w) // 2
    for i, color in enumerate(colors):
        x = x_start + i * (bar_w + gap)
        lcd.fill_rect(x, y_pos, bar_w, bar_h2, color)
        lcd.show()
        time.sleep(0.1)

def draw_status(lines):
    """Mostra 3 linhas centrais de status (com fallback 'N/A')."""
    lcd.fill_rect(0, 40, 320, 90, lcd.BLACK)
    y = 60
    for txt in lines:
        if not txt or txt.strip() == "":
            txt = "N/A"
        lcd.write_text(txt, 20, y, 2, lcd.WHITE)
        y += 25
    lcd.show()

# ---------------------------------------------------------------
#  SEQUÊNCIA DE ARRANQUE (BOOT)
# ---------------------------------------------------------------

def lcars_boot_sequence():
    """Executa a sequência de arranque completa LCARS."""
    backlight_flicker()
  #  animate_header()
    time.sleep(0.8)
    draw_header("EMBY")
    backlight_flicker_soft()
    draw_bottom_bars()
    draw_status(["Server: Emby", "IP: 192.168.1.100", "Status: Online"])
    backlight_flicker_soft()
    time.sleep(1.0)

# ---------------------------------------------------------------
#  MODO ATIVO (DADOS DO LINUX)
# ---------------------------------------------------------------

# ---------------------------------------------------------------
#  MODO ATIVO (DADOS DO LINUX) — com persistência de estado
# ---------------------------------------------------------------

def lcars_active_mode():
    """Lê dados via USB e mantém o último estado por 10s antes de limpar."""

    import sys, time

    draw_header("EMBY")
    draw_bottom_bars()
    draw_status(["Server: Waiting", "IP: ---", "Status: Idle"])

    last_update = time.ticks_ms()
    last_data = ["Server: N/A", "IP: N/A", "Status: N/A"]

    while True:
        try:
            line = sys.stdin.readline().strip()
            if line:
                parts = line.split("|")
                while len(parts) < 3:
                    parts.append("N/A")
                draw_status(parts)
                last_data = parts
                last_update = time.ticks_ms()
            else:
                # Se passaram mais de 10s sem novas mensagens → mostrar N/A
                if time.ticks_diff(time.ticks_ms(), last_update) > 10000:
                    draw_status(["Server: N/A", "IP: N/A", "Status: N/A"])
                    last_update = time.ticks_ms()
                else:
                    # mantém o último estado no ecrã
                    draw_status(last_data)
            time.sleep(0.2)

        except Exception as e:
            lcd.fill_rect(0, 40, 320, 90, lcd.BLACK)
            lcd.write_text("Erro:", 20, 60, 2, lcd.RED)
            lcd.write_text(str(e)[:20], 20, 85, 2, lcd.WHITE)
            lcd.show()
            time.sleep(2)

# ---------------------------------------------------------------
#  EXECUÇÃO PRINCIPAL
# ---------------------------------------------------------------

lcars_boot_sequence()   # arranque animado LCARS
lcars_active_mode()     # modo ativo em loop
