# to_remember — OpenCode, HuggingFace i OpenSpec

Notatnik na powrót po przerwie. Wszystko poniżej zostało sprawdzone w praktyce w tym
projekcie, nie przepisane z dokumentacji.

Ostatnia weryfikacja: **2026-11-19**

---

## 1. Środowisko — co gdzie jest

| Element | Wersja | Gdzie / jak sprawdzić |
| --- | --- | --- |
| Node.js | 22.23.5 | `node --version` |
| npm | 11.14.1 | `npm --version` |
| OpenCode | 2.3.2 | `opencode --version` |
| OpenSpec | 2.1.0 | `openspec --version` |
| Python | 3.13.5 | `python --version` |
| System | Windows 10/11 | — |

Kluczowe ścieżki:

```
opencode.jsonc                      konfiguracja projektu (models, agents, commands)
~/.config/opencode/opencode.jsonc   konfiguracja globalna
~/.local/share/opencode/log/        logi (C:\Users\<user>\.local\share\opencode\log\)
%APPDATA%\npm\                      globalne pakiety npm (npm -g)
%APPDATA%\openspec\config.json      globalna konfiguracja OpenSpec
.agents/skills/                     skille OpenSpec w repo (od 2.0)
openspec/specs/                     specyfikacje
openspec/changes/                   propozycje zmian w toku
```

**Zapamiętaj:** `opencode.jsonc` przeładowuje się sam po zapisie. Nie trzeba restartować
OpenCode po zmianie konfiguracji, agentów, skilli czy komend.

---

## 2. OpenCode — minimum na start

### Tryby pracy

| Tryb | Do czego |
| --- | --- |
| **Plan** | Analizuje, czyta, proponuje. Nie zmienia plików. |
| **Build** | Implementuje, edytuje, commituje (za zgodą). |

Przełączasz agentem. Jeśli chcesz najpierw ustalić plan, a potem dać mu wykonać — to dwie
osobne sesje, nie jedna.

### Klawisze, które naprawdę się używa

| Skrót | Działanie |
| --- | --- |
| `/models` lub `ctrl+x` → `m` | wybór modelu |
| `f2` | następny ostatnio używany model (szybkie cheap ↔ balanced) |
| `ctrl+t` | cykl wariantów rozumowania (`low` / `medium` / `high`) |
| `shift+tab` | następny agent |
| `ctrl+x` → `a` | lista agentów |

Leader to `ctrl+x`. Podmienia się w `cli.json` (osobny plik od `opencode.jsonc`).

**Uwaga:** `/models` nie przyjmuje argumentu. `/models flash-balanced` nic nie zrobi — trzeba
wybrać z listy. Model da się zmienić z poziomu agenta przez API:

```powershell
opencode api post "/api/session/$env:OPENCODE_SESSION_ID/model" `
  --data '{"model":{"providerID":"huggingface","id":"flash-balanced"}}'
```

### Z linii poleceń

```powershell
opencode run --model huggingface/flash-balanced "zadanie"
opencode run --agent hard "zadanie"
opencode run --model "huggingface/pro-hard#high" "zadanie"
opencode api get /api/model          # inspekcja katalogu modeli
opencode service status              # stan usługi w tle
```

**Pułapka:** `opencode api` czasem rozwiązuje lokalizację do katalogu domowego
(`C:\Users\<user>`) zamiast do projektu — wtedy nie widzi projektowego `opencode.jsonc`.
Jeśli wynik wygląda „ubogo", to prawdopodobnie ten przypadek. `opencode run` działa
poprawnie w kontekście projektu.

### Struktura `opencode.jsonc`

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "huggingface/flash-balanced",   // domyślny model NOWYCH sesji
  "providers": { "<id>": { "models": { "<alias>": { "modelID": "...", "limit": {}, "cost": {} } } } },
  "agents":    { "<id>": { "mode": "primary", "model": "provider/model" } },
  "commands":  { "<id>": { "template": "$ARGUMENTS", "agent": "...", "model": "...", "subagent": true } },
  "instructions": [".github/instructions/*.md"]
}
```

Rzeczy, o których się zapomina:

- `model` na górze działa tylko na **nowe** sesje. Bieżąca sesja trzyma swój model.
- Klucz w `models` to alias OpenCode; `modelID` to to, co leci do providera.
- `limit` i `cost` **trzeba ustawić jawnie** dla modeli spoza katalogu models.dev.
  Bez tego OpenCode przyjmie fallback **200 000 kontekstu / 32 000 output** — czyli dokładnie
  ten limit, który dusi darmowe modele.
- Skille/komendy w `.opencode/` i `.agents/` przeładowują się bez restartu.

---

## 3. HuggingFace Inference Providers — jak to działa naprawdę

Konfiguracja providera w OpenCode:

```
provider ID: huggingface
baseURL:     https://router.huggingface.co/v1
```

### `auto` nie jest modelem — to router

Bez sufiksu request idzie przez router HF, który pod spodem używa **OpenRouter** i wybiera
providera według trzech kryteriów: ceny efektywnej, szybkości i niezawodności.

**Czego router NIE bierze pod uwagę: kwantyzacji.** To jest najważniejsza rzecz w całej
tej notatce. Ten sam model w `fp8` i w `fp4` to pod względem jakości kodu dwa różne modele.
Router może cicho przerzucić Cię na `fp4`, bo jest tańszy.

Przykład z `DeepSeek-V4.1-Flash-1017` (stan 2026-11-19):

| Provider | Cena in/out | Kwantyzacja | tok/s | TTFT |
| --- | --- | --- | --- | --- |
| deepinfra | $0.098 / $0.294 | fp8 | 117 | 776 ms |
| novita | $0.12 / $0.48 | fp8 | 106 | 1463 ms |
| cloudflare | $0.10 / $0.60 | — | 96 | 2127 ms |
| coreweave | $0.30 / $1.20 | fp8 | **228** | 391 ms |
| relace | $0.12 / $0.50 | **fp4** | 133 | 553 ms |
| wafer | $0.036 / $0.50 | **mxfp4** | 155 | 351 ms |

### Sufiksy wyboru providera

| Zapis | Efekt |
| --- | --- |
| `deepseek-ai/DeepSeek-V4.1-Flash-1017` | domyślny routing: balans ceny/szybkości/niezawodności |
| `deepseek-ai/DeepSeek-V4.1-Flash-1017:cheapest` | najtaniej — **uwaga: wpada na fp4** |
| `deepseek-ai/DeepSeek-V4.1-Flash-1017:fastest` | najwyższy throughput |
| `deepseek-ai/DeepSeek-V4.1-Flash-1017:deepinfra` | **tylko ten provider** |

Sufiks działa w każdym kliencie — także tam, gdzie da się ustawić wyłącznie nazwę modelu.
Dlatego wystarczy wkleić go do `modelID` w `opencode.jsonc`.

**Cena przypięcia: brak failoveru.** Przypięty provider nigdy nie jest zastępowany — jeśli
padnie, dostajesz błąd, a nie ciche przełączenie. Jeśli to przeszkadza, lepsze rozwiązanie:
wyłącz providerów fp4/mxfp4 na [hf.co/settings/inference-providers](https://hf.co/settings/inference-providers)
i używaj wersji bez sufiksu. Wtedy router sam omija słabsze kwantyzacje, zachowując failover.

### Jak sprawdzić dane, gdy trzeba

```powershell
# kto obsługuje dany model (status live/error)
curl "https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4-Pro?expand[]=inferenceProviderMapping"

# pełny katalog z cenami, kontekstem, kwantyzacją i uptime per provider
curl "https://router.huggingface.co/v1/models"

# katalog modeli OpenCode (context, limit, koszt)
curl "https://models.dev/api.json"
```

`router.huggingface.co/v1/models` to jedyne źródło, które podaje **kwantyzację i uptime per
provider**. models.dev tego nie ma, a jego ceny dla wpisów „auto" potrafią być nieprawdziwe
(np. `DeepSeek-V4-Pro` wyceniony na $0.44/$0.87, gdy najtańszy realny provider to $0.90/$1.50).

---

## 4. Modele — co jest dostępne i jak wybierać

### Najważniejsza lekcja: model ≠ okno kontekstu

`DeepSeek V4.1 Flash Free` i `DeepSeek V4.1 Flash 1017` to te same wagi. Różni je hosting:

| | Free | Płatny |
| --- | --- | --- |
| Kontekst | **200 000** | **1 048 576** |
| Max output | **32 000** | 384 000 |
| Koszt | $0 | $0.30 / $1.20 |

200K i 32K to nie cechy modelu, tylko limity darmowego tieru. To tłumaczy, dlaczego darmowy
model „zapomina" i „przerywa w połowie" na dużym repo — nie jest głupszy, tylko ma pełny dysk.

### Kontekst a rozmiar tego projektu

Orientacyjnie: **~10 tokenów na linię Pythona**.

| Co | Znaki | Tokeny |
| --- | --- | --- |
| `src/` (22 pliki, 10 691 linii) | 459K | **~127K** |
| + skrypty `*.py` w roocie | 179K | ~50K |
| + `kitty-specs/` | 42K | ~12K |
| razem | 680K | **~189K** |

Czyli `src/` zajmuje **64% okna darmowego modelu** i **12% okna modeli 1M**. Przełączanie się
między 200K a 1M to nie kosmetyka.

### Pułapka Kimi

Kimi poza topowymi modelami ma **256K**, nie 1M:

| Model | Kontekst | In / Out |
| --- | --- | --- |
| Kimi K2.5 Free | 256K | free |
| Kimi K2.7 Code | **256K** | $0.95 / $4 |
| Kimi K3 | 1.00M | $3 / $15 |
| Kimi K3.1 Pro | 1.05M | $2 / $10 |

Kimi K2.7 Code jest świetny do kodu, ale przy repo na ~189K tokenów 256K to tylko 35% zapasu
więcej niż darmowy model. **Dla tego projektu wygrywa DeepSeek V4 — bo ma 1M w rozsądnej cenie.**

### Trzy profile wybrane dla tego projektu

| Alias | Model | Kontekst | In / Out | Kiedy |
| --- | --- | --- | --- | --- |
| `flash-cheap` | V4.1 Flash 1017 `:deepinfra` | 1.05M | $0.098 / $0.294 | masowa robota, drobnice, skrypty |
| `flash-balanced` | V4.1 Flash 1017 `:coreweave` | 1.05M | $0.30 / $1.20 | domyślny do codziennej pracy |
| `pro-hard` | V4 Pro 0813 `:deepinfra` | 1.05M | $1.30 / $2.60 | astronomia, schemat bazy, refaktory |

Wszystkie trzy na **fp8**. Do wyboru w `/models`, a `pro-hard` jest też podpięty pod agenta
`hard` (`shift+tab`) i komendę `/hard <zadanie>` (subagent w tle, nie brudzi głównego kontekstu).

### Ile to realnie kosztuje

Zmierzone na tej sesji: 319K input, 19,6K output, **4,79M odczytów cache**, koszt **$0,032**.
Cache robi całą różnicę przy długich rozmowach.

| Poziom | Koszt work package'a |
| --- | --- |
| `flash-cheap` | ~$0.10 |
| `flash-balanced` | ~$0.20–0.40 |
| `pro-hard` | ~$0.30–0.60 za pojedyncze trudne zadanie |

Koszt i tokeny bieżącej sesji:

```powershell
opencode api get "/api/session/$env:OPENCODE_SESSION_ID"
```

### Jak ocenić model w 10 minut

Zamiast czytać benchmarki, daj konkretne zadanie i sprawdź trzy rzeczy:

1. Czy **najpierw przeczytał** istniejące moduły, czy wymyślił nowe?
2. Czy dotknął **wszystkich warstw** (parser → DB → logika → UI → test), czy tylko najłatwiejszej?
3. Czy **cokolwiek uruchomił**, czy tylko stwierdził, że działa?

Odpowiedzi „tak, tak, tak" oznaczają, że model jest wart swojej ceny. Dwie z trzech — problem
jest w specyfikacji, nie w modelu.

---

## 5. OpenSpec

### Instalacja i aktualizacja

```powershell
npm install -g "@fission-ai/openspec@latest"
openspec --version
```

Wymagania Node według wersji — to realna blokada, nie kosmetyka:

| Wersja OpenSpec | Wymaga Node |
| --- | --- |
| ≤ 1.15.0 | ≥ 20.19.0 |
| 1.16.0 – 1.17.x | ≥ 22.12.0 |
| 2.0.0+ | ≥ 22.20.0 |

### Co się zmieniło w 2.0 (ważne po przerwie)

- **Tylko skille, koniec z plikami komend.** `/opsx-propose` już nie istnieje. Skill wołasz
  jako `/openspec-propose`. Jeśli pamiętasz `opsx` z 1.x — to jest ta różnica.
- **Jedna wspólna kopia skilli** w `.agents/skills/` zamiast kopii per narzędzie.
  `openspec update` usuwa stare pliki komend.
- `delivery` przestało cokolwiek robić (nadal jest akceptowane).

### Workflow

Schemat `spec-driven`: **proposal → specs → design → tasks**.

| Skill | Do czego |
| --- | --- |
| `openspec-explore` | tryb myślenia: doprecyzowanie problemu, zanim cokolwiek zaproponujesz |
| `openspec-propose` | tworzy change z proposal.md, design.md, tasks.md w jednym kroku |
| `openspec-apply-change` | implementuje zadania z tasks.md |
| `openspec-update-change` | poprawia artefakty change'a, gdy decyzje się zmienią |
| `openspec-sync-specs` | przenosi delta-specs do głównych specs bez archiwizowania |
| `openspec-archive-change` | zamyka change i aktualizuje główne specyfikacje |

W praktyce: explore → propose → apply → archive. `update` i `sync` są do korekt w trakcie.

### CLI

```powershell
openspec list                     # aktywne change'y
openspec show <change>            # szczegóły
openspec validate --all           # walidacja
openspec status                   # stan artefaktów change'a
openspec update . --dry-run       # co zmieni aktualizacja, bez zapisu
openspec config list              # globalna konfiguracja
openspec config profile core      # profil workflow
```

### Profile workflow

- `core` — 6 workflow: `propose`, `explore`, `apply`, `update`, `sync`, `archive`.
- `custom` — wybierasz sam. Uwaga: profil „custom" z 1.x migrował bez `update`, co dawało
  ostrzeżenie przy każdym `openspec update`. Przełączenie na `core` to naprawia.
- Dodatkowo dostępne: `new`, `continue`, `ff`, `bulk-archive`, `verify`, `onboard` —
  do dorzucenia przez `openspec config profile`.

### Pułapki, które nas trafiły

1. **Pusty katalog `openspec/` nie jest śledzony przez git.** Bez plików w `specs/` i
   `changes/` repo po klonie nie będzie miał struktury. Rozwiązanie: `.gitkeep` w każdym
   z katalogów (już dodane).
2. **Spec Kitty dopisało `.opencode/` do `.gitignore`.** Przez to wygenerowane skille nie
   trafiały do repo. Od 2.0 skille siedzą w `.agents/` — sprawdź `git check-ignore -v <plik>`,
   jeśli coś „nie chce się" zacommitować.
3. **Instalator zgłasza „Detected new tool: GitHub Copilot"**, bo widzi katalog `.github/`.
   Można ignorować, jeśli nie używasz Copilota.
4. **Telemetria jest włączona** (w `%APPDATA%\openspec\config.json` siedzi `anonymousId`).

---

## 6. Zasady pracy z agentem (wyniesione z tej rozmowy)

- **Weryfikuj, nie wierz.** Agent potrafi napisać „gotowe". Sprawdzaj `git status`,
  `git check-ignore`, `openspec update --dry-run`, realny request do providera.
- **Nie zgaduj nazw pakietów i flag.** `npm view <pkg> version engines`, `--help` — zawsze
  przed instalacją. Pakiet `openspec` na npm to atrapa `0.0.0`; właściwy to `@fission-ai/openspec`.
- **Commituj etapami.** Każdy krok jako osobny commit z jasnym komunikatem. Rollback pojedynczej
  decyzji jest wtedy trywialny.
- **Zadania muszą być sprawdzalne.** „Altitude liczy się poprawnie" to życzenie.
  „Altitude zgadza się z kolumną Z arkusza dla 5 obiektów" to specyfikacja.
- **Arkusz xlsm jest golden masterem.** Zawiera policzone czasy wschodów, tranzyty, separacje
  Księżyca. To darmowy oracle testowy — nie trzeba go wymyślać, wystarczy porównać.
- **Nie zmieniaj modelu w połowie work package'a.** Skończ WP, potem przełącz.
- **Plan i Build to osobne sesje.** Najpierw plan bez edycji, potem implementacja.
- **Duże repo czytaj celowo.** Przy 1M kontekstu kusi, żeby wrzucić wszystko. Lepiej czytać
  wybrane moduły — mniej szumu, mniej tokenów, lepsze skupienie.

---

## 7. Jak zacząć nowy projekt w tym środowisku

Kolejność ma znaczenie — punkty 1–3 muszą być przed pierwszym uruchomieniem agenta, inaczej
będziesz poprawiać konfigurację po fakcie.

### Krok 0 — sprawdź środowisko

```powershell
node --version      # ≥ 22.20.0 dla OpenSpec 2.x
npm --version
python --version
opencode --version
openspec --version
```

### Krok 1 — OpenSpec w projekcie

```powershell
cd <projekt>
npm install -g "@fission-ai/openspec@latest"    # jeśli jeszcze brak lub jest stary
openspec init . --tools opencode
openspec config profile core
openspec update .
openspec validate --all
```

`openspec init` utworzy `openspec/{specs,changes,changes/archive}` oraz skille w `.agents/skills/`.

### Krok 2 — zabezpiecz strukturę w git

```powershell
# puste katalogi nie są śledzone — dodaj markery
New-Item -ItemType File openspec/specs/.gitkeep
New-Item -ItemType File openspec/changes/.gitkeep
New-Item -ItemType File openspec/changes/archive/.gitkeep

# upewnij się, że skille NIE są ignorowane (puste = dobrze)
git check-ignore -v .agents/skills/openspec-propose/SKILL.md
```

Jeśli `.agents/` albo `.opencode/` jest w `.gitignore`, usuń tę linię. Wygenerowane pliki mają
być w repo — inaczej workflow znika po klonie i trzeba pamiętać o `openspec update`.

### Krok 3 — `opencode.jsonc`

Minimalna wersja: `$schema`, `model`, `instructions`. Wersja pełna z profilami modeli — patrz
sekcja 4. Wzór do skopiowania:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "huggingface/flash-balanced",
  "providers": {
    "huggingface": {
      "models": {
        "flash-cheap": {
          "name": "V4.1 Flash · deepinfra (cheap)",
          "modelID": "deepseek-ai/DeepSeek-V4.1-Flash-1017:deepinfra",
          "limit": { "context": 1048576, "output": 384000 },
          "cost": { "input": 0.098, "output": 0.294 }
        },
        "flash-balanced": {
          "name": "V4.1 Flash · coreweave (fast)",
          "modelID": "deepseek-ai/DeepSeek-V4.1-Flash-1017:coreweave",
          "limit": { "context": 1048576, "output": 384000 },
          "cost": { "input": 0.3, "output": 1.2 }
        },
        "pro-hard": {
          "name": "V4 Pro 0813 · deepinfra (hard)",
          "modelID": "deepseek-ai/DeepSeek-V4-Pro-0813:deepinfra",
          "limit": { "context": 1048576, "output": 384000 },
          "cost": { "input": 1.3, "output": 2.6 }
        }
      }
    }
  },
  "agents": {
    "hard": {
      "description": "Hard tasks: astronomy math, database schema, multi-file refactors",
      "mode": "primary",
      "model": "huggingface/pro-hard"
    }
  },
  "commands": {
    "hard": {
      "description": "Run a task on V4 Pro in a separate subagent",
      "template": "$ARGUMENTS",
      "agent": "general",
      "model": "huggingface/pro-hard",
      "subagent": true
    }
  },
  "instructions": [".github/instructions/*.md"]
}
```

Po zapisie sprawdź, czy aliasy się zarejestrowały:

```powershell
opencode run --model huggingface/flash-balanced "Reply with exactly: OK"
```

Jeśli odpowiada — provider jest przypięty poprawnie i limit 1M przyjęty.

### Krok 4 — podłącz HuggingFace

```
/connect        # wybierz Hugging Face i wklej token
/models         # sprawdź, czy widzisz modele huggingface/*
```

Klucz jest trzymany przez OpenCode, nie w zmiennych środowiskowych — dlatego `$env:HF_TOKEN`
może być pusty, a modele i tak działają. Sprawdzenie, które nie wymaga czytania sekretów:
`opencode run --model huggingface/...`.

### Krok 5 — pierwszy commit

```powershell
git add .gitignore opencode.jsonc .agents openspec
git commit -m "chore: initialize OpenSpec and OpenCode model profiles"
```

### Krok 6 — pierwszy change

1. `openspec-explore` — przepracuj pomysł, zanim cokolwiek powstanie.
2. `openspec-propose` — powstaje proposal, design i tasks.
3. `openspec validate --all` — sprawdź, czy artefakty są spójne.
4. `openspec-apply-change` — implementacja.
5. `openspec-archive-change` — zamknięcie i aktualizacja głównych specs.

### Krok 7 — rytm pracy

| Moment | Ruch |
| --- | --- |
| Nowy pomysł | `openspec-explore` → `openspec-propose` |
| Zwykła implementacja | `flash-balanced` |
| Astronomia, schemat, refaktor | `shift+tab` → agent `hard` |
| Jedno trudne pytanie w tanim zadaniu | `/hard <zadanie>` |
| Koniec etapu | commit + `openspec validate --all` |
| Koniec zmiany | `openspec-archive-change` |

---

## 8. Ściągawka

```powershell
# --- OpenCode ---
opencode run --model huggingface/flash-balanced "..."   # jednorazowo, z wybranym modelem
opencode run --agent hard "..."                         # jednorazowo, z agentem
opencode service status                                 # stan usługi w tle
opencode api get "/api/session/$env:OPENCODE_SESSION_ID" # koszt i tokeny sesji

# --- OpenSpec ---
openspec init . --tools opencode
openspec config profile core
openspec update . --dry-run
openspec list
openspec validate --all
openspec archive <change-name>

# --- diagnostyka providerów ---
curl "https://router.huggingface.co/v1/models"          # ceny, kontekst, kwantyzacja, uptime
curl "https://huggingface.co/api/models/<repo>?expand[]=inferenceProviderMapping"
npm view "@fission-ai/openspec" version engines          # wersje i wymagania

# --- git ---
git check-ignore -v <plik>                               # dlaczego plik nie wchodzi do repo
git status --short --untracked-files=all
```

| Skrót | Działanie |
| --- | --- |
| `/models` / `ctrl+x m` | wybór modelu |
| `f2` | cykl ostatnich modeli |
| `ctrl+t` | wariant rozumowania |
| `shift+tab` | następny agent |
| `ctrl+x a` | lista agentów |

---

## 9. Stan tego projektu (2026-11-19)

- Node podniesiony z 22.11.0 do **22.23.5**, OpenSpec z 1.3.1 do **2.1.0**, profil **core**.
- OpenCode ma trzy przypięte profile: `flash-cheap`, `flash-balanced` (domyślny), `pro-hard`.
- Agent `hard` i komenda `/hard` podpięte pod V4 Pro.
- **`kitty-specs/` jest zamrożone** — misja `001-better-astro-photos`, wszystkie 5 WP
  w stanie `approved`. Zostawione jako zapis historyczny, nie jako bieżące źródło prawdy.
  Marker: `kitty-specs/README.md`.
- `openspec/` gotowe, zero change'ów. Skille w `.agents/skills/`.
- Commity graniczne: `1462398` (wprowadzenie OpenSpec + profile modeli), `e39270e` (migracja do 2.1.0).
- Niezacommitowane: `.github/instructions/UserInterface.md` i `instructions.md` — edycje użytkownika.
