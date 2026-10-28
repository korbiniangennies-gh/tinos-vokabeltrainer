# Vokabeldaten

`vokabeln_greenline1.csv` ist die Master-Liste (Green Line 1, alle Units). Die App (`index.html`) bekommt ihre Vokabeln daraus.

## Spalten

| Spalte | Bedeutung |
|---|---|
| `id` | Feste Kennung, z. B. `U1.S2.door`. **Nie ändern** – daran hängt Tinos Lernstand. Bei neuen Zeilen leer lassen, sie wird automatisch vergeben. |
| `unit` | `GRS`, `U1` … `U4`, `MS1`, `AC1`, `AC2`, `TR` |
| `station` | `CI`, `S1`, `S2`, `S3`, `ST`, `UT`, `CO` (bei Zusatzteilen leer) |
| `englisch` | Wie im Buch. `(to)` = optional, `(= we are)` = Alternative, `(pl)` wird ausgeblendet. |
| `deutsch` | Bedeutungen mit `;` trennen – in der App erscheint `/`. |
| `weitere_antworten` | Zusätzlich akzeptierte Antworten, mit `\|` getrennt (z. B. `soccer\|bicycle`). |
| `quelle` | `Green Line 1` oder `eigene` |

## Ändern / ergänzen

1. CSV auf github.com bearbeiten (geht auch am Handy) und auf `main` speichern.
2. Der Workflow „Vokabeln aktualisieren“ überträgt die Änderung automatisch in `index.html`.

Lokal geht das auch mit `python3 tools/build_vocab.py`.

Welche Units Tino gerade lernt, stellt man in der App unter **📚 Lernstoff wählen** ein (Aktiv / Wiederholen / Aus). Dafür muss nichts an der CSV geändert werden.

Das Original-PDF von Klett liegt wegen des Urheberrechts nicht im (öffentlichen) Repo, sondern auf OneDrive.
