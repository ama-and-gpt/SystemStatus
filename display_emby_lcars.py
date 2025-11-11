"""
Display Emby LCARS Panel (modo ativo)
-------------------------------------
Autor: Ama
Versão: 1.0a
Descrição:
    Versão estática do painel LCARS para o display Waveshare RP2350 1.47".
    Recebe texto dinâmico pela porta série (USB) vindo de um script Linux.
    Formato de entrada:
        "linha1|linha2|linha3"
    Exemplo:
        echo "Server: Emby|IP: 192.168.1.101|Status: Online" > /dev/ttyACM0
"""

from lcd import LCD_1inch47
import time, math, sys

lcd = LCD_1inch47()
lcd.fill(lcd.BLACK)
bar_h = 25

# --- Cabeçalho LCARS fixo ---
def draw_header(title="EMBY"):
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

# --- Barras inferiores fixas ---
def draw_bottom_bars():
    bar_w, bar_h2, gap, y_pos = 60, 10, 10, 140
    colors = [lcd.BLUE, lcd.CYAN, lcd.GREEN, lcd.YELLOW]
    total_w = (bar_w * 4) + (gap * 3)
    x_start = (320 - total_w) // 2
    for i, color in enumerate(colors):
        x = x_start + i * (bar_w + gap)
        lcd.fill_rect(x, y_pos, bar_w, bar_h2, color)
    lcd.show()

# --- Linhas de status dinâmicas ---
def draw_status(lines):
    lcd.fill_rect(0, 40, 320, 90, lcd.BLACK)  # limpa a área central
    y = 60
    for txt in lines:
        lcd.write_text(txt, 20, y, 2, lcd.WHITE)
        y += 25
    lcd.show()

# --- Inicializa layout base ---
draw_header("EMBY")
draw_bottom_bars()
draw_status(["Server: Waiting", "IP: ---", "Status: Idle"])

# --- Loop principal (aguarda dados via USB) ---
while True:
    try:
        # Lê uma linha vinda do Linux (p.ex. echo "linha1|linha2|linha3")
        line = sys.stdin.readline().strip()
        if not line:
            continue

        # Divide o texto recebido nas três linhas
        parts = line.split("|")
        while len(parts) < 3:
            parts.append("")  # garante 3 entradas

        draw_status(parts)

    except Exception as e:
        # Em caso de erro, mostra a mensagem brevemente
        lcd.fill_rect(0, 40, 320, 90, lcd.BLACK)
        lcd.write_text("Erro:", 20, 60, 2, lcd.RED)
        lcd.write_text(str(e)[:20], 20, 85, 2, lcd.WHITE)
        lcd.show()
        time.sleep(2)
