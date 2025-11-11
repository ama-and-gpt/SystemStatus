# LCARS Display – Raspberry Pi Pico RP2350 + LCD 1.47”

Simple system status display
**Versão / Version:** v2.0 Final – Outubro / October 2025  
**Autor / Author:** Ama B.  
**Licença / License:** MIT  

---

## 🇵🇹 Introdução
Este projeto implementa um painel inspirado na interface LCARS (*Library Computer Access/Retrieval System*, conhecida da série *Star Trek*), utilizando um microcontrolador **Raspberry Pi Pico RP2350** e um **ecrã Waveshare LCD 1.47”**.  
O sistema exibe informações provenientes de um servidor Linux (ex. hostname, IP, uptime), comunicando via **USB CDC (dual)** ou **UART física**.  

## 🇬🇧 Introduction
This project implements an LCARS-style panel (Library Computer Access/Retrieval System from *Star Trek*), using a **Raspberry Pi Pico RP2350** and a **Waveshare 1.47” LCD**.  
It displays real-time data from a Linux server (hostname, IP, uptime) via **USB CDC (dual)** or **physical UART** connection.

---

## 🇵🇹 Hardware
### Componentes principais
| Função | Pino Pico | Descrição |
|---------|-----------|-----------|
| BL (Backlight) | 21 | PWM para controlo de brilho |
| DC | 16 | Data/Command |
| RST | 20 | Reset do LCD |
| MOSI | 19 | SPI MOSI |
| SCK | 18 | SPI Clock |
| CS | 17 | Chip Select |

O ecrã é alimentado a 3.3 V e comunica por SPI0.  
O pino BL é controlado por **PWM**, permitindo ajustar o brilho.

### 🇬🇧 Hardware
| Function | Pico Pin | Description |
|-----------|-----------|-------------|
| BL (Backlight) | 21 | PWM brightness control |
| DC | 16 | Data/Command |
| RST | 20 | LCD Reset |
| MOSI | 19 | SPI MOSI |
| SCK | 18 | SPI Clock |
| CS | 17 | Chip Select |

The display operates at 3.3 V and communicates via SPI0.  
The BL pin is driven by PWM to control brightness.

---

## 🇵🇹 Software no Pico
O firmware **MicroPython Dual CDC** permite:
- Comunicação USB (entrada/saída via `/dev/ttyACM0`)
- Comunicação UART alternativa (TX=GP0, RX=GP1)
- Execução automática de `main.py` (modo LCARS ativo)

O ficheiro `main.py` implementa:
- Efeito de *lâmpada fluorescente* no backlight  
- Cabeçalho LCARS com cantos convexos e título centrado  
- Barras coloridas inferiores  
- Linhas de estado dinâmicas com *fallback* “N/A”  
- Ajuste automático de brilho conforme a hora do dia  

### 🇬🇧 Pico Software
The **Dual CDC MicroPython firmware** provides:
- USB communication (read/write on `/dev/ttyACM0`)
- Optional UART (TX=GP0, RX=GP1)
- Auto-launch of `main.py` (active LCARS mode)

The `main.py` implements:
- Fluorescent lamp effect on backlight  
- LCARS header with convex corners and centered title  
- Bottom colored bars  
- Dynamic status lines with “N/A” fallback  
- Automatic brightness adjustment based on system time  

---

## 🇵🇹 Software no Linux
O script `send_status_linux.sh` recolhe:
- Nome do servidor (hostname)  
- IP ativo (rota para 8.8.8.8)  
- Uptime compacto (`3h21m`, `2d4h`, etc.)  

Depois envia via serial:
```
Server: <host>|IP: <ip>|Uptime: <uptime>
```

### Instalação:
```bash
sudo install -m 755 send_status_linux.sh /usr/local/bin/send_status_linux.sh
```

### Atualização automática (cron):
```bash
*/1 * * * * /usr/local/bin/send_status_linux.sh
```
→ Atualiza o LCD a cada minuto.

### 🇬🇧 Linux Software
The `send_status_linux.sh` script collects:
- Server name (hostname)  
- Active IP (via route to 8.8.8.8)  
- Compact uptime (`3h21m`, `2d4h`, etc.)

Then it sends through the serial interface:
```
Server: <host>|IP: <ip>|Uptime: <uptime>
```

#### Installation:
```bash
sudo install -m 755 send_status_linux.sh /usr/local/bin/send_status_linux.sh
```

#### Automatic update (cron):
```bash
*/1 * * * * /usr/local/bin/send_status_linux.sh
```
→ Refreshes the display every minute.

---

## 🇵🇹 Funcionamento
1. O Pico arranca com efeito de luz e apresenta o cabeçalho LCARS.  
2. Se não houver dados, mostra “N/A”.  
3. Quando recebe informação do Linux, atualiza as três linhas de estado.  
4. Se não receber dados durante 10 s, volta a mostrar “N/A”.  
5. O brilho ajusta-se automaticamente conforme a hora local.

### 🇬🇧 Operation
1. Pico boots with lighting effect and displays LCARS header.  
2. If no data is received, “N/A” is shown.  
3. When new data arrives from Linux, the three status lines update.  
4. If no data for 10 s, display returns to “N/A”.  
5. Brightness adjusts automatically based on local time.

---

## 🇵🇹 Créditos e Licença
**Autor:** Ama B.  
**Licença:** MIT – livre utilização e modificação, mediante referência ao autor.  

## 🇬🇧 Credits & License
**Author:** Ama B.  
**License:** MIT – free use and modification with author attribution.

---

📎 Para mais detalhes e código completo (`main.py` + `send_status_linux.sh`), consultar o PDF do projeto:  
**LCARS_Display_Project.pdf**
