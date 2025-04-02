#!/bin/bash

# Eğer PORT değişkeni ayarlanmadıysa, varsayılan port olarak 8000 kullan
if [ -z "$PORT" ]; then
  PORT=8000
fi

# Gunicorn'u belirtilen port ile başlat
exec gunicorn --bind 0.0.0.0:$PORT run:app 