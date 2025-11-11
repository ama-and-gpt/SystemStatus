#!/usr/bin/env bash
# Emby LCARS → Pico (USB CDC ou UART) V1.4
# Envia: "Server: <host>|IP: <ip>|Status/Uptime: <uptime>"

set -euo pipefail

# 1) Detecta porta (prefere /dev/ttyACM*, senão /dev/ttyUSB*)
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

# 2) Prepara parâmetros (podes forçar pelo ambiente)
SERVER_NAME="${SERVER_NAME:-$(hostname)}"

# IP ativo (sem docker/lo): route para 8.8.8.8 é simples e robusto
IP_ADDR="$(ip route get 8.8.8.8 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src"){print $(i+1); exit}}')"
[[ -z "$IP_ADDR" ]] && IP_ADDR="N/A"

# Uptime legível
#UPTIME="$(uptime -p 2>/dev/null | sed 's/^up //')"
#[[ -z "$UPTIME" ]] && UPTIME="N/A"

# ---------- 3. Uptime compacto e locale-independente ----------
# Lê segundos desde boot e formata como y/mo/w/d/h/m/s (máx. 3 componentes)
secs_total="$(awk '{print int($1)}' /proc/uptime 2>/dev/null || echo 0)"

y=$((secs_total/31557600)); r=$((secs_total%31557600))
mo=$((r/2592000));         r=$((r%2592000))
w=$((r/604800));           r=$((r%604800))
d=$((r/86400));            r=$((r%86400))
h=$((r/3600));             r=$((r%3600))
m=$((r/60));               s=$((r%60))

UPTIME=""
append_part() { local v="$1" sfx="$2"; [[ "$v" -gt 0 ]] && UPTIME="${UPTIME}${v}${sfx}"; }

# junta no máx. 3 partes não-zero (ex.: 2w1d13h)
count=0
for part in "y:$y" "mo:$mo" "w:$w" "d:$d" "h:$h" "m:$m" "s:$s"; do
  key=${part%%:*}; val=${part##*:}
  if [[ $val -gt 0 ]]; then
    append_part "$val" "$key"
    count=$((count+1))
    [[ $count -ge 3 ]] && break
  fi
done

# fallback se tudo zero (arranque muito recente)
[[ -z "$UPTIME" ]] && UPTIME="0s"

# corta para não estourar largura do LCD
UPTIME="${UPTIME:0:12}"


# 3) Mensagem (Pico espera pipe | e CRLF)
MSG="Server: ${SERVER_NAME}|IP: ${IP_ADDR}|Uptime: ${UPTIME}"

# 4) Configura a porta (stty ajuda em alguns adaptadores; no CDC também é inofensivo)
if command -v stty >/dev/null 2>&1; then
  stty -F "$DEV" 115200 -echo -icrnl -inlcr -ixon -ixoff 2>/dev/null || true
fi

# 5) Envia com CRLF e força flush
printf "%s\r\n" "$MSG" > "$DEV"
sync

# 6) Eco opcional
echo "Enviado para $DEV → $MSG"
