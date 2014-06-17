# Droogle - wyszukiwarka dla plików w formacie Drill

## Składowe

- `base.py` - zawiera wszystkie kluczowe komponenty i funkcje
- `index.py` - wrapper indeksujący zawartość plików do dalszego przeszukiwania
- `query.py` - wrapper udostępniający interfejs do wykonywania zapytań

## Używanie

1. Przygotowanie plików

    Pierwszym krokiem jest przygotowanie plików, które Droogle będzie przeszukiwać. W katalogu Droogle należy utworzyć folder o dowolnej nazwie i umieścić w nim pliki z rozszerzeniem `.txt`. Mogą to być dowolne pliki tekstowe, których fragmenty są oddzielone są podwójnymi znakami nowej linii.

2. Indeksowanie

    W celu zindeksowania katalogu należy uruchomić skrypt `index.py`. Jeśli znajdzie on więcej niż jeden katalog, to poprosi o wybranie tego, który powinien zindeksować. W przeciwnym wypadku zindeksuje jedyny znaleziony katalog.

    Podczas indeksowania w katalogu tworzone są dodatkowe pliki. Zawierają one wszystkie dane potrzebne do pracy wyszukiwarki. Nazwa zindeksowanego katalogu jest też zapisywana do konfiguracji, a kolejne zapytania korzystają właśnie z tego indeksu.

3. Wykonywanie zapytań

    Plik `query.py` udostępnia prosty interfejs do wykonywania zapytań. Po jego uruchomieniu program pyta w pętli o kolejne frazy do wyszukania, aż do napotkania pustej frazy. Samo uruchamianie jest zwykle najdłużej trwającym procesem, ponieważ wymaga wczytania danych z indeksu do pamięci. Samo wyszukiwanie jest szybsze.

    Po wprowadzeniu frazy skrypt wyświetli skonfigurowaną liczbę najlepszych trafień. Ze względu na specyfikę algorytmu dla niewystępujących nigdzie fraz wyświetlone zostaną przypadkowe, błędne wyniki, więc wszystko, co program wypisuje należy zweryfikować zdrowym rozsądkiem (zdrowy rozsądek nie jest dostarczany wraz z programem).

## Konfiguracja

Konfiguracja jest przechowywana w pliku `config.json` w formacie JSON. Obsługiwane są następujące wartości:

- `index` - nazwa indeksu, w którym będzie przeprowadzane wyszukiwanie
- `results` - ilość najlepszych wyników do wyświetlenia przy wyszukiwaniu

Konfiguracja jest wykorzystywana tylko i wyłącznie przez wrappery `index.py` oraz `query.py`, a nie przez główny kod wyszukiwarki.