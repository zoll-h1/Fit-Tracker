#!/bin/bash
# get-tunnel-url.sh — prints the Cloudflare Tunnel public URL

echo "Waiting for tunnel URL..."
for i in $(seq 1 30); do
    URL=$(docker compose logs cloudflared 2>/dev/null | grep -oP 'https://[a-zA-Z0-9\-]+\.trycloudflare\.com' | tail -1)
    if [ -n "$URL" ]; then
        echo ""
        echo "✅ Your FitTracker is live at:"
        echo "   $URL"
        echo ""
        echo "🔗 Admin panel: $URL/admin"
        echo ""
        exit 0
    fi
    sleep 2
done

echo "❌ Could not find tunnel URL. Check logs with: docker compose logs cloudflared"
