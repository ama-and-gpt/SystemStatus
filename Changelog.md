🧾 LCARS Display – Changelog

Autor / Author: Ama B.
Plataforma: Raspberry Pi Pico RP2350 + LCD 1.47”
Firmware: MicroPython Dual CDC
Licença: MIT

🟩 v1.0 – Conceito Inicial (Set 2025)

Primeira implementação do cabeçalho LCARS com curvas convexas.

Introdução do efeito lâmpada fluorescente no backlight.

Exibição fixa de texto “EMBY” e barras inferiores coloridas.

Código estático sem comunicação com Linux.

🟨 v1.1 – Modo Ativo e Comunicação Linux (Out 2025)

Implementado modo ativo via USB CDC com leitura contínua (sys.stdin).

Adicionado script Linux inicial (send_status_linux.sh) para envio de status.

Introduzido fallback automático “N/A” após 10 s sem dados.

Primeira sincronização entre servidor Linux e display LCARS.

🟧 v1.2 – Estabilidade e Brilho Automático

Otimização do loop de atualização (reduzido flicker).

Adicionado controlo automático de brilho com base na hora local (modo noturno).

Documentação PDF técnica e README bilingue criados.

Revisão estética do cabeçalho LCARS e animações suavizadas.

🟦 v1.3 – Script Linux Avançado

send_status_linux.sh atualizado para v1.3:

Deteção automática de porta /dev/ttyACM* / /dev/ttyUSB*.

IP ativo via ip route get 8.8.8.8.

Formato compacto de uptime (3h21m, 2w1d13h).

Limite de comprimento do texto para evitar overflow no LCD.

🟪 v1.4 – Uptime Locale-Independente (Final)

Substituição completa do cálculo de uptime:

Agora lê diretamente /proc/uptime.

Suporte completo a years, months, weeks, days, hours, minutes, seconds.

Saída sempre em ASCII puro (ex.: 1y3mo5d, 2w1d13h).

Corrigido bug visual “weeks, 1[]” em displays com fontes limitadas.

Confirmada compatibilidade total com cron (atualização a cada minuto).

Estabilização final → versão pronta para publicação no GitHub.
