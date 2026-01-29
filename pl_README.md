#### README w innych językach
[English](https://github.com/sanitywarden/roblox-fishing-simulator-bot#readme)

# roblox-fishing-simulator-bot
To repozytorium zawiera prostego bota/skrypt w języku Python na systemy Windows oraz macOS, który automatyzuje proces łowienia ryb w grze Roblox o nazwie Fishing Simulator.

> Projekt ten powstał z własnej ciekawości i należy go stosować wyłącznie w celach edukacyjnych. Używanie botów i/lub skryptów automatyzujących pogarsza wrażenia z gry dla całej społeczności graczy i powinno się tego unikać.

> Korzystanie z tego skryptu jest najprawdopodobniej sprzeczne z wytycznymi Roblox i może skutkować blokadą konta (banem) w przypadku wykrycia. Używasz go na własne ryzyko. Zawsze przestrzegaj warunków świadczenia usług gry oraz platformy.

## Funkcje

* Działa na systemach Windows (`windows.py`) oraz macOS (`macos.py`)
* Wykrywa elementy gry za pomocą rozpoznawania kolorów pikseli
* Losowe odstępy czasowe kliknięć LPM, aby naśladować interakcję człowieka 
* Automatyczne wstrzymanie pracy, gdy ekwipunek jest pełny
* Możliwość zatrzymania (domyślnie `q`) lub wstrzymania (domyślnie `p`) skryptu
* Możliwość ręcznego zresetowania bota w przypadku błędu/zawieszenia (domyślnie `r`)
* Możliwość wyświetlenia informacji o aktualnej sesji łowienia w terminalu (domyślnie `i`)

## Wydajność
Z moich pomiarów wynika, że bot wyciąga średnio jedną rybę co 10–12 sekund. Daje to wynik około 300 do 360 złowionych ryb na godzinę.

## Wymagania 
- Roblox
- Python (przetestowane na 3.12)

## Jak zainstalować
### Używając `git`

1. Sklonuj/pobierz to repozytorium
```
git clone https://github.com/sanitywarden/roblox-fishing-simulator-bot
```

2. Otwórz folder `roblox-fishing-simulator-bot` w terminalu i zainstaluj odpowiednie pakiety Pythona w zależności od Twojego systemu operacyjnego.

#### Windows
```
pip install -r windows_requirements.txt
```
Po zainstalowaniu pakietów przygotuj Roblox, dołącz do gry Fishing Simulator i uruchom komendę `python windows.py` lub `python3 windows.py` w terminalu. Jeśli żadna z nich nie działa, oznacza to, że nie masz zainstalowanego interpretera Python na swoim systemie. Zainstaluj go i wróć do tego kroku później.

#### MacOS
```
pip install -r macos_requirements.txt
```

Po zainstalowaniu pakietów Twój Mac najprawdopodobniej nie pozwoli jeszcze na uruchomienie tego skryptu. Musisz najpierw nadać mu odpowiednie uprawnienia, ponieważ system macOS jest bardziej restrykcyjny.

Przejdź do `Ustawienia Systemowe > Prywatność & Bezpieczeństwo > Dostępność` i dodaj aplikację `Terminal` do listy. Zrób to samo w sekcji `Nagrywanie Ekranu`.

Teraz przygotuj Roblox, dołącz do gry Fishing Simulator i uruchom komendę `python macos.py` lub `python3 macos.py`. Jeśli żadna z nich nie działa, oznacza to, że nie masz zainstalowanego interpretera Python na swoim systemie. Zainstaluj go i wróć do tego kroku później.