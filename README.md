# GIS Support Cloud

Link do strony projektu: https://gis-support.pl/gis-support-cloud/

## I. Opis

Projekt Cloud jest rozwiążaniem, które umożliwia szybsze wdrażanie aplikacji GISowych u klienta. Jest bogatą nakładką na Postgres wraz z PostGISem, która umożliwia zarządzanie w wygodniejszy sposób warstwami, obiektami w warstwach, użytkownikami, uprawnieniami oraz stylami. Tworzy też warstwę abstrakcji, która umożliwia szybsze rozwijanie aplikacji opratych na REST API. Jest również kompatybilny z QGIS - umożliwia pełne zarządzanie danymi (zgodnie z uprawnieniami) bezpośrednio z załadowanych warstw PostGIS.

Główne cechy projektu:

- modułowość - moduły nie są w żaden sposób od siebie zależne, można dodawać nowe, odpinać istniejące, wszystko z poziomu jednego pliku konfiguracyjnego

- skalowalność - przez zastosowanie Dockera istnieje możliwość replikacji kontenerów

- przewidywalność - 100% funkcjonalności pokryta jest testami jednostkowymi oraz integracyjnymi

- przejrzystość - zarówno kodu jak i dokumentacji

---

## II. Wymagania

- Docker 19.03+

- Docker Compose 1.21+

- Minimalne wymagania sprzętowe: 2GB RAM + 2vCPU + 50GB SSD

---

## III. Instalacja

1. Należy ustawić odpowiednie parametry w pliku .env w głównym katalogu aplikacji.

2. Należy wykonać polecenie:

```
docker-compose -f docker-production.yml up -d --build
```
