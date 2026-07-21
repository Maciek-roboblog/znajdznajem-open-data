#!/bin/sh
set -eu
install -d -m700 /root/.ssh
touch /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
for key in \
'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICbX3ZkV9BsIYJXCxzqqkZtYMZPSqJEPusW/vP39iLZZ maciek@DESKTOP-87NNF0E' \
'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIw6SmmV2V9z2mtA06DLYzCR0QFEgxQxAIZkqp0KAGrq ubuntu@znajdznajem'
do grep -qxF "$key" /root/.ssh/authorized_keys || printf '%s\n' "$key" >> /root/.ssh/authorized_keys; done
printf 'PermitRootLogin prohibit-password\nPubkeyAuthentication yes\n' > /etc/ssh/sshd_config.d/00-rootkey.conf
chown -R root:root /root/.ssh
sshd -t
systemctl reload ssh
echo '>>> GOTOWE <<<'
