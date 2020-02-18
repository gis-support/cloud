# GIS Support Cloud

##  I. Wstęp

Projekt Cloud jest rozwiążaniem, które umożliwia szybsze wdrażanie aplikacji GISowych u klienta. Jest bogatą nakładką na Postgres wraz z PostGISem, która umożliwia zarządzanie w wygodniejszy sposób warstwami, obiektami w warstwach, użytkownikami, uprawnieniami oraz stylami. Tworzy też warstwę abstrakcji, która umożliwia szybsze rozwijanie aplikacji opratych na REST API. Jest również kompatybilny z QGIS - umożliwia pełne zarządzanie danymi (zgodnie z uprawnieniami) bezpośrednio z załadowanych warstw PostGIS.

Główne cechy projektu:

* modułowość - moduły nie są w żaden sposób od siebie zależne, można dodawać nowe, odpinać istniejące, wszystko z poziomu jednego pliku konfiguracyjnego

* skalowalność - przez zastosowanie Dockera istnieje możliwość replikacji kontenerów

* przewidywalność - 100% funkcjonalności pokryta jest testami jednostkowymi oraz integracyjnymi

* przejrzystość - zarówno kodu jak i dokumentacji

## 1. Architektura
Aplikacja składa się z 3 kontenerów:

* db - jest to baza danych Postgres 12 + PostGIS 3.0 od kartozy, zmodyfikowana na nasze potrzeby (obsługa skryptu inicjalnego na więcej niż jednej bazie, ze względu na środowisko testowe). Podczas inicjalizacji kontenerów uruchamiany jest skrypt init.sql, który tworzy tabelę do styli (żeby QGIS je odpowiednio wczytał) oraz tworzy grupy użytkowników.

* api - jest to API we Flasku oparte na Pythonie 3.7.3. Podpięty jest również Swagger dla dokumentacji. Po uruchomieniu kontenerów mamy również możliwość uruchomienia testów jednostkowych i integracyjnych.

* redis - baza potrzebna do trzymania tokenów logowania w API, żeby nie zaśmiecać instancji postgresowej.


## 2. Moduły

Podstawa aplikacji składa się z 4 głównych modułów:

* auth - Jest to moduł autoryzacji oparty na Redisie, JWT oraz postgresowych użytkownikach z hasłami. Tokeny są potrzebne do korzystania ze wszystkich modułów aplikacji. Moduł tworzy 10-minutowe tokeny odświeżane z każdym requestem o kolejne 10 minut.

* layers = Jest to moduł warstw, którego głównym zadaniem jest tworzenie warstw, zarządzanie nimi, ich nazwami, kolumnami oraz stylami. Enpoint dodawania nowej przyjmuje jedynie pliki - obecnie wszystkie wektorowe obsługiwane przez GDAL.

* features - Jest to CRUD do obiektów w warstwie zgodnie z uprawnieniami.

* permissions - Składa się tylko z dwóch endpointów, jeden do listowania macierzy użytkowników i warstw (w celu stworzenia tabeli z uprawnieniami) oraz drugi do edycji uprawnienia dla danego użytkownika w danej warstwie.

## 3. Dodatkowe moduły

Na potrzeby wdrożenia projektu RDOŚ Lublin została stworzona "wtyczka" do API, która zawiera wszystkie wydzielone funkcjonalności. Póki co:

* attachments - tabela do przechowywania załączników z Owncloud wraz z adnotacjami, który załącznik do której grupy użytkowników.

---

## II. Development

1. Wymagania:

* Docker 19.03+

* Docker Compose 1.21+

2. Aby uruchomić aplikację należy uruchomić komendę:
```
docker-compose up
```
3. Aby przeprowadzić testy, należy mieć uruchomione środowisko oraz uruchomić komendę:
```
docker exec -it cloud-api tests
```
4. Aby przejrzeć helper do testów:

```
docker exec -it cloud-api tests -h
```
Można dowiedzieć się z niego że możemy praktykować Test Driven Development uruchamiając poszczególne grupy testów, np:
```
docker exec -it cloud-api tests -g permissions
```
5. Każdy moduł powinien się składać z:

* plików dokumentacyjnych pisanych w konwencji:
```
docs.[nazwa_encji].[ewentualnie_drugi_czlon_encji].[metoda].yml
```

* pliku _routings.py_ zawierający Blueprint wraz z endpointami

* pliku _test.py_ z testami wszystkich enpointów

* (opcjonalnie) pliku _models.py_ z modelami w Peewee dla modułu

6. Bazy domyślnie są w trybie __PERSISTENT__ także w celu flushowania obu baz prócz komendy:
```
docker-compose down -v
```
Należy pozbyć się persistent directories, czyli:
```
sudo rm -rf ./docker/db/postgres_data
sudo rm -rf ./docker/db/redis_data
```
7. Sugerowana instrukcja developmentu:

* Dodajemy nowy moduł z plikiem _routings.py_ z endpointami zwracającymi puste dane + opcjonalnie _models.py_

* Podpinamy moduł do _create.py_ (jeśli RDOŚ to _rdos/\_\_init\_\_.py_)

* Dodajemy nową grupę testów do _pytest.ini_

* Dodajemy w nowym module plik _test.py_ z testami pobierającymi te puste dane

* Zapisujemy w testach co potrzebujemy i uruchamiamy ciągle nową grupę testów w celu bieżącego developmentu

* Tworzymy i podpinamy dokumentację

* Uruchamiamy wszystkie testy

8. Wszystkie metody odnośnie bazy/warstw dostępne są w klasach Cloud oraz Layer w _helpers/cloud.py_ + _helpers/layer.py_ + _helpers/style.py_ lub _db/general.py_

---

## III. Deployment

1. Wymagania:

* Docker 19.03+

* Docker Compose 1.21+

2. Należy ustawić odpowiednie parametry w pliku .env w głównym katalogu aplikacji.

3. Należy wykonać polecenie:

```
docker-compose -f docker-production.yml up -d --build
```
