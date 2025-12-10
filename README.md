# 🎼 **ArtiFux: Constraint-Based Counterpoint Composer**

**Course:** *CMPE 353 — Principles of AI*  
**Project Type:** *Algorithmic Composition & Constraint Satisfaction (CSP)*

ArtiFux is an AI-powered music engine that composes counterpoint by transforming **Baroque counterpoint rules** (1600–1750) into **formal constraints**. Given a *Cantus Firmus*, the system generates a stylistically accurate **counterpoint melody** using classical *Species Counterpoint* principles.

>It separates theory rules into **Hard Constraints** (strict) and **Soft Constraints** (aesthetic scoring), then uses a **Backtracking CSP solver** to explore the search space and select the most musical solution.

<br>

# 🎵 Music Theory Meets AI

The core engine, `baroque_engine.py`, is inspired by J.J. Fux’s *Gradus ad Parnassum* and encodes real counterpoint discipline through computational logic.

<br>


## 1️⃣ **Hard Constraints (Mandatory)**
Violating any of these results in **immediate pruning**. The engine discards the candidate before continuing the search.

| 🎛️ Rule | Function | Description |
|---------|-----------|----------|
| 🚫 **Parallel Fifths & Octaves** | `hc_parallel_fifths_octaves` | Prevents voices from moving in the same direction into perfect 5ths or octaves. |
| 🎹 **Strong-Beat Consonance** | `hc_consonant_interval` | Strong beats must use consonant intervals (Unison, 3rd, 5th, 6th, Octave). |
| 📉 **Suspension Prep & Resolution** | `hc_suspension_resolution` | Dissonances must be prepared and resolved downwards by stepwise motion. |
| ⚠️ **Forbidden Melodic Intervals** | `hc_no_augmented_melodic` | Prohibits non-vocal intervals such as tritones, major 7ths, and augmented leaps. |

<br>

## 2️⃣ **Soft Constraints & Heuristic Scoring**

### A. **Explicit Soft Constraints**
These rules are applied to completed partial solutions to evaluate their quality.

| 🌟 Rule | Score | Description |
|---------|------|----------|
| ⚡ **Accented Dissonance** | +5 | Correct preparation and resolution of suspensions are highly rewarded. |
| 🌉 **Passing Tone** | +2 | Stepwise motion connecting consonances on weak beats. |
| 🔄 **Contrary Motion** | +2 | Rewarded when voices move in opposite directions (independence). |
| ❌ **Hidden Parallels** | -5 | Penalizes hidden parallels reached by a leap (skip). |
| 🤏 **Close Position** | +1 | Rewards keeping the voices within a range of 16 semitones. |

---

### B. **Candidate Ordering Heuristics**
Used within `get_valid_candidates()` to prioritize the search tree order.

| 🔍 Heuristic | Score | Description |
|--------------|------|----------|
| 🔄 **Contrary Motion** | +3 | Contrary motion candidates are tried first. |
| 🚶 **Stepwise Motion** | +2 | Prioritizes smooth, conjunct melodic lines. |
| 🤝 **Imperfect Consonances** | +1 | Imperfect consonances (3rds, 6ths) are preferred over perfect ones. |
| 🎹 **Scale Filtering** | -1000 | Massive penalty for notes outside the key scale. |
| 🐇 **Leap Penalty** | -2 | Large leaps are discouraged in the ordering. |

<br>

# 📂 **Project Structure**

This project uses a modular structure: an AI engine + multiple composition scripts + output folders.

## **`codes/` — Source Files**

* **`baroque_engine.py`** 🧠 — CSP solver, theory rules, Backtracking.
* **`generate_gameOfThrones.py`** ⚔️ — Baroque–orchestral GoT arrangement.
* **`generate_hijo_masterpiece.py`** 🌕 — Advanced *Hijo de la Luna* Masterpiece.
* **`generate_hijo_splitchoir.py`** 🎤 — Stereo-separated Soprano/Bass choir.
* **`generate_love_pledge.py`** 💍 — Baroque-style *Love Pledge* arrangement.
* **`generate_pasdedeux.py`** 🩰 — Analysis + generation for *Pas de Deux*.



## 📦 **Output Folders**

* **`GoT_baroque_result/`** — GoT MIDI/PDF/PNG.
* **`HijoDeLuna_baroque_result/`** — Masterpiece + Split Choir versions MIDI/PDF/PNG.
* **`LovePledge_baroque_result/`** — Love Pledge MIDI/PDF/PNG.
* **`PasDeDeux_baroque_result/`** — PasDeDeux MIDI/PDF/PNG.


<br>

# 🚀 Installation & Quick Start

## **1. Install Requirements**

```bash
pip install -r requirements.txt
```

## **2. Configure MuseScore** (for PDF export)

### Windows

```python
musescore_path = "C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
```

### macOS

```python
musescore_path = "/Applications/MuseScore 4.app/Contents/MacOS/mscore"
```

## **3. Run a Script**

```bash
python codes/generate_gameOfThrones.py
python codes/generate_hijo_masterpiece.py
```

<br>

# 📤 Output Types

| File               | Meaning                            |
| ------------------ | ---------------------------------- |
| 🎹 `.mid`          | Playable MIDI file                 |
| 🎼 `.pdf`          | Score rendered via MuseScore       |
| 📊 `_analysis.png` | Visual explanation of AI reasoning |

<br>

# 🧠 Algorithm Pipeline

1. Key Detection
2. Candidate Generation
3. Hard Constraint Filtering (Pruning)
4. Soft Constraint Scoring & Sorting
5. **Backtracking Search** for best path

---

