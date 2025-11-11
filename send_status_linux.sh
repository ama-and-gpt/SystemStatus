#!/usr/bin/env bash
# =========================================================
# LCARS Display → Raspberry Pi Pico / RP2350
# ---------------------------------------------------------
# Autor / Author: Ama B.
# Versão / Version: 1.3 (Outubro / October 2025)
# Licença / License: MIT
# ---------------------------------------------------------
# Descrição / Description:
#  - Recolhe dados do sistema Linux e envia via porta serial
#    (USB CDC /dev/ttyACM0 ou UART /dev/ttyUSB0)
#  - Compatível com o firmware Dual CDC MicroPython no Pico
#  - Atualiza o painel LCARS com:
#       • Nome do servidor / Server name
#       • IP ativo / Active IP
#       • Uptime compacto / Compact uptime
# ---------------------------------------------------------
# Exemplo:
#   ./send_status_linux.sh
#   printf "Server: Emby|IP: 192.168.1.100|Uptime: 2w1d13h\r\n" > /dev/ttyACM0
# =========================================================

set -euo pipefail

# ---------- 1. Deteção automática de porta ----------
detect_port() {
  for p in /dev/ttyACM* /dev/ttyUSB*; do
    [[ -e "$p" && -c "$p" ]] && echo "$p" && return 0
  done
  return 1
}

DEV="${1:-$(detect_port || true)}"
if [[ -z "${DEV:-}" ]]; then
  echo "Erro: não encontrei /dev/ttyACM* nem /dev/ttyUSB*." >&2
  exit 1
fi

# ---------- 2. Informação do sistema ----------
SERVER_NAME="${SERVER_NAME:-$(hostname)}"

# IP ativo (ignora loopback/docker)
IP_ADDR="$(ip route get 8.8.8.8 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src"){print $(i+1); exit}}')"
[[ -z "$IP_ADDR" ]] && IP_ADDR="N/A"

# ---------- 3. Uptime compacto com suporte a weeks, months e years ----------
raw_uptime="$(uptime -p 2>/dev/null | sed 's/^up //')"
if [[ -z "$raw_uptime" ]]; then
  UPTIME="N/A"
else
  raw_uptime="$(echo "$raw_uptime" | tr -d ',' | tr -s ' ')"
  UPTIME=$(echo "$raw_uptime" \
    | sed -E \
      -e 's/ year(s)?/y/g' \
      -e 's/ month(s)?/mo/g' \
      -e 's/ week(s)?/w/g' \
      -e 's/ day(s)?/d/g' \
      -e 's/ hour(s)?/h/g' \
      -e 's/ minute(s)?/m/g' \
      -e 's/ second(s)?/s/g' \
      -e 's/ //g')
  # Limita comprimento máximo (para não sair do LCD)
  UPTIME="${UPTIME:0:12}"
fi

# ---------- 4. Monta mensagem ----------
MSG="Server: ${SERVER_NAME}|IP: ${IP_ADDR}|Uptime: ${UPTIME}"

# ---------- 5. Configura porta ----------
if command -v stty >/dev/null 2>&1; then
  stty -F "$DEV" 115200 -echo -icrnl -inlcr -ixon -ixoff 2>/dev/null || true
fi

# ---------- 6. Envia mensagem ----------
printf "%s\r\n" "$MSG" > "$DEV"
sync

# ---------- 7. Eco local ----------
echo "Enviado para $DEV → $MSG"
