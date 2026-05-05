#!/bin/bash
case "$1" in
  "/start")
    echo "👋 Привет! Я локальный помощник Komorok."
    ;;
  "/site")
    echo "🌐 https://komorok.ru"
    ;;
  "/help")
    echo "Доступные команды: /start, /site, /help"
    ;;
  *)
    echo "Неизвестная команда. Попробуй /help"
    ;;
esac
