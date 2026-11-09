# Deploy Tupa: push -> pull no VPS -> rebuild
git push origin main
ssh kvm8 'cd /root/tupa && git pull && docker compose build --no-cache && docker compose up -d && docker compose ps && docker compose logs --tail=20'
