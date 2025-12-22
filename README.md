# 🎼 ArtiFux: Constraint-Based Counterpoint Composer

**Course:** CMPE 353 — Principles of AI  
**Project Type:** Algorithmic Composition & Constraint Satisfaction (CSP)

ArtiFux is an AI-powered music engine that composes **Baroque-style counterpoint** by transforming historical counterpoint rules (1600–1750) into formal computational constraints.

Given a **Cantus Firmus** (base melody), the system generates a stylistically accurate counterpoint melody using **Species Counterpoint** principles inspired by **J.J. Fux’s _Gradus ad Parnassum_**.

The engine separates music theory into:
- **Hard Constraints** (strict, mandatory rules)
- **Soft Constraints** (heuristic, aesthetic preferences)

A **Backtracking CSP solver** explores the search space and selects the most musical solution.

<br>


## 🎵 Music Theory Meets AI

The core engine, `baroque_engine.py`, encodes authentic Baroque counterpoint discipline into algorithmic logic.  
Each generated melody respects traditional voice-leading rules, dissonance treatment, and cadence structure.

<br>


## 1️⃣ Hard Constraints (Mandatory)

Violating any of these constraints causes **immediate pruning** of the candidate note.

| Rule | Function | Description |
|----|----|----|
| Scale Adherence | Domain Generation | Notes must belong to the selected scale |
| Parallel Fifths & Octaves | `check_parallels` | Prevents parallel perfect intervals |
| Strong Beat Consonance | `check_harmonic_validity` | No dissonance on strong beats |
| Suspension Resolution | `check_suspension` | Dissonances must resolve downward |
| Forbidden Intervals | `check_melodic_validity` | Tritones, 7ths, large leaps forbidden |
| Final Cadence | `check_final_cadence` | Ends on octave or unison |

<br>

## 2️⃣ Soft Constraints (Heuristic Scoring)

Soft constraints guide the search toward musically superior solutions.

| Rule | Score |
|----|----|
| Accented Dissonance | +5 |
| Contrary Motion | +2 |
| Passing / Stepwise Motion | +2 |
| Close Vocal Range | +1 |
| Hidden Parallels | -5 |

<br>


## 📂 Project Structure

### 📁 codes/
- `baroque_engine.py` — Core CSP solver
- `generate_gameOfThrones.py`
- `generate_hijo_masterpiece.py`
- `generate_hijo_splitchoir.py`
- `generate_love_pledge.py`
- `generate_pasdeduex.py`

### 📦 Output Folders
- `GoT_baroque_result/`
- `HijoDeLuna_baroque_result/`
- `LovePledge_baroque_result/`
- `PasDeDeux_baroque_result/`

<br>


## 🚀 Installation

```bash
pip install -r requirements.txt
```

Required:
- music21
- midiutil

<br>


## ▶️ Basic Usage

```python
from codes.baroque_engine import BaroqueEngine

cantus = [60, 62, 64, 65, 67, 69, 71, 72]

engine = BaroqueEngine(
    cantus_firmus=cantus,
    scale_root=60,
    scale_type="major",
    num_bars=8
)

melody = engine.generate_counterpoint()
engine.save_to_midi("output.mid")
```

<br>


# 🎼 Algorithm: CSP Baroque Composer (Backtracking)

This algorithm follows the principle:

**“Define rules first, then search for the best musical path.”**

<br>


## 1️⃣ Initialization
```plaintext
CLASS BaroqueEngine:
- Inputs:
  - cantus_firmus
  - scale_root
  - scale_type
  - num_bars

PROCESS:
1. Generate valid scale notes  
   ScaleNotes = [60, 62, 64, 65, 67, ...]

2. Start CSP search  
   RESULT = Backtrack(current_melody=[])

---
```
## 2️⃣ Backtracking Core
```plaintext
FUNCTION Backtrack(current_melody):

IF length(current_melody) == length(cantus_firmus):
- IF final cadence valid → RETURN solution
- ELSE → RETURN failure
```
<br>


## 3️⃣ Domain Generation
```plaintext

current_index = len(current_melody)  
cf_note = cantus_firmus[current_index]  
possible_notes = GetAllNotesInScale()
```
<br>


## 4️⃣ Hard Constraint Filtering (Pruning)
```plaintext

FOR each candidate_note IN possible_notes:

- IF melodic interval > 12 semitones → SKIP
- IF strong beat AND harmonic interval dissonant → SKIP
- IF parallel 5th or octave detected → SKIP
- IF unresolved suspension → SKIP

ADD candidate_note TO valid_candidates
```
<br>


## 5️⃣ Soft Constraint Sorting (Heuristics)
```plaintext

SORT valid_candidates by SCORE:

- Contrary motion → +2
- Stepwise motion → +2
- Suspension preparation → +5
- Hidden parallel → -5
```
<br>


## 6️⃣ Recursive Search
```plaintext

FOR each selected_note IN valid_candidates:

- current_melody.ADD(selected_note)
- result = Backtrack(current_melody)

IF result != failure:
- RETURN result

ELSE:
- current_melody.REMOVE_LAST()

RETURN failure
```
<br>


## 7️⃣ Constraint Helper Functions
```plaintext

FUNCTION IsDissonant(note1, note2):
- interval = |note1 - note2| % 12
- Consonant intervals: unison, 3rd, 5th, 6th, octave
- Otherwise → dissonant

FUNCTION CheckParallels(n1, n2, cf1, cf2):
- Detects parallel fifths and octaves
```
<br>


## 📤 Outputs

| File | Description |
|----|----|
| .mid | MIDI playback |
| .pdf / .musicxml | Sheet music |
| _Analiz.png | Constraint analysis |

<br>

🎼 ArtiFux demonstrates how classical Baroque counterpoint can be modeled as a Constraint Satisfaction Problem and solved using heuristic backtracking search.
