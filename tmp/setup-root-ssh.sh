#!/bin/sh
# Bootstrap: dodaje nasze klucze SSH do roota (test box "przesiadka").
# Idempotentny - mozna odpalac wielokrotnie. Zawiera TYLKO klucze publiczne (bezpieczne).
set -e
install -d -m700 /root/.ssh
touch /root/.ssh/authorized_keys

add_key() {
  grep -qF "$1" /root/.ssh/authorized_keys 2>/dev/null || printf '%s\n' "$1" >> /root/.ssh/authorized_keys
}
add_key "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICbX3ZkV9BsIYJXCxzqqkZtYMZPSqJEPusW/vP39iLZZ maciek@DESKTOP-87NNF0E"
add_key "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIw6SmmV2V9z2mtA06DLYzCR0QFEgxQxAIZkqp0KAGrq ubuntu@znajdznajem"
chmod 600 /root/.ssh/authorized_keys

# Pozwol rootowi logowac sie kluczem (ale nie haslem)
echo 'PermitRootLogin prohibit-password' > /etc/ssh/sshd_config.d/00-rootkey.conf

if sshd -t 2>/dev/null; then
  systemctl reload ssh 2>/dev/null || systemctl reload sshd 2>/dev/null || service ssh reload 2>/dev/null || true
  RELOAD="sshd-reloaded"
else
  RELOAD="SSHD-CONFIG-BLAD-nie-przeladowano"
fi

echo ">>> GOTOWE: klucze=$(grep -cE '^(ssh-|ecdsa-)' /root/.ssh/authorized_keys) host=$(hostname) $RELOAD <<<"
