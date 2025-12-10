import random
import sys
import os
import subprocess
import collections
from midiutil import MIDIFile

# --- KÜTÜPHANE KONTROLLERİ ---
print("--- SİSTEM KONTROLÜ ---")
try:
    from baroque_engine import UniversalBaroqueSolver 
    print("[OK] Baroque Engine yüklü.")
except ImportError:
    pass 

try:
    import matplotlib.pyplot as plt
    GRAPH_AVAILABLE = True
    print("[OK] Matplotlib yüklü.")
except ImportError:
    GRAPH_AVAILABLE = False

try:
    import music21
    from music21 import instrument, clef, note
    MUSIC21_AVAILABLE = True
    print("[OK] Music21 yüklü.")
except ImportError:
    MUSIC21_AVAILABLE = False

print("-----------------------\n")

# --- 1. MELODİK YAPI (GENİŞLETİLMİŞ) ---

# OSTINATO
ostinato_pattern = [
    (55, 0.5), (48, 0.5), (51, 0.5), (53, 0.5), 
    (55, 0.5), (48, 0.5), (51, 0.5), (53, 0.5)
]

# A BÖLÜMÜ
theme_main = [
    (55, 3.0), 
    (55, 1.5), (48, 0.5), (51, 0.5), (53, 0.5), 
    (55, 3.0),
    (55, 1.5), (48, 0.5), (51, 0.5), (53, 0.5), 
    (50, 3.0), (50, 3.0) 
]

# B BÖLÜMÜ
theme_b = [
    (60, 3.0),
    (60, 1.5), (58, 0.5), (61, 0.5), (63, 0.5), 
    (60, 3.0),
    (60, 1.5), (55, 0.5), (51, 0.5), (53, 0.5),
    (55, 3.0), (55, 3.0)
]

# CODA (YENİ BÖLÜM - FINAL)
theme_coda = [
    (55, 1.0), (53, 1.0), (51, 1.0), # G F Eb (İniş)
    (50, 3.0),                       # D (Bekle)
    (55, 1.0), (53, 1.0), (51, 1.0), 
    (48, 3.0),                       # C (Bekle)
    (60, 3.0), (55, 3.0),            # High C -> G (Dramatik)
    (48, 6.0)                        # Low C (Final Vuruş)
]

# INTRO
intro_rhythm = [
    (48, 1.0), (55, 1.0), (55, 1.0), 
    (48, 1.0), (55, 1.0), (55, 1.0),
    (48, 1.0), (55, 1.0), (55, 1.0),
    (48, 1.0), (55, 1.0), (55, 1.0)
]

# --- 2. ENSTRÜMAN LİSTESİ ---
INSTRUMENTS = {
    "Cello Solo": 42, "Dulcimer": 15, "String Ensemble": 48,  
    "Violin Solo": 40, "Choir Aahs": 52, "French Horn": 60,      
    "Trombone": 57, "Tuba": 58, "Timpani": 47, "War Drums": 0          
}

# --- 3. MİKSER AYARLARI ---
MIXER_SETTINGS = {
    "Cello Solo":      {"pan": 64, "reverb": 60},
    "Dulcimer":        {"pan": 40, "reverb": 50},
    "Violin Solo":     {"pan": 80, "reverb": 70},
    "String Ensemble": {"pan": 64, "reverb": 90},
    "Choir Aahs":      {"pan": 64, "reverb": 110},
    "French Horn":     {"pan": 30, "reverb": 80},
    "Trombone":        {"pan": 90, "reverb": 80},
    "Tuba":            {"pan": 70, "reverb": 70},
    "Timpani":         {"pan": 64, "reverb": 90},
    "War Drums":       {"pan": 64, "reverb": 50}
}

# --- 4. YARDIMCI FONKSİYONLAR ---
def get_human_touch(inst_name, duration):
    if inst_name in ["Dulcimer", "War Drums"]:
        return 0.0, 0 
    timing = random.uniform(-0.02, 0.02)
    vel_var = random.randint(-5, 10)
    return timing, vel_var

# --- 5. MIDI OLUŞTURMA ---
def save_orchestrated_midi(song_structure, arrangement, filename):
    midi = MIDIFile(len(arrangement["melody"] + arrangement["rhythm"] + arrangement["background"]) + 1)
    track = 0
    START_BPM = 125 
    
    all_insts = arrangement["melody"] + arrangement["rhythm"] + arrangement["background"]
    mel_data = []
    
    for inst_name in all_insts:
        channel = track if track < 9 else track + 1
        if channel > 15: channel = 0
        
        midi.addTrackName(track, 0, inst_name)
        midi.addProgramChange(track, channel, 0, INSTRUMENTS.get(inst_name, 0))
        midi.addTempo(track, 0, START_BPM)
        
        settings = MIXER_SETTINGS.get(inst_name, {"pan": 64, "reverb": 50})
        midi.addControllerEvent(track, channel, 0, 10, settings["pan"])
        midi.addControllerEvent(track, channel, 0, 91, settings["reverb"])
        
        time = 0
        
        for section_idx, section in enumerate(song_structure):
            is_intro = (section == intro_rhythm)
            is_climax = (section == theme_b)
            is_finale = (section == theme_coda) # Final bölümü
            
            notes_to_play = []

            # 1. RİTİM (Dulcimer)
            if inst_name == "Dulcimer":
                if is_intro:
                    notes_to_play = section
                else:
                    total_dur = sum([d for n, d in section])
                    measures = int(total_dur / 3.0)
                    root = 48 
                    if section == theme_b: root = 53
                    
                    for _ in range(measures):
                        notes_to_play.append((root + 7, 0.5)) 
                        notes_to_play.append((root, 0.5))
                        notes_to_play.append((root + 3, 0.5))
                        notes_to_play.append((root + 5, 0.5))
                        notes_to_play.append((root + 7, 0.5))
                        notes_to_play.append((root, 0.5))

            # 2. MELODİ (Çello)
            elif inst_name == "Cello Solo":
                if is_intro:
                     notes_to_play = [(0, sum([d for n, d in section]))]
                else:
                    notes_to_play = section

            # 3. BACKGROUND
            elif inst_name in ["String Ensemble", "Choir Aahs", "French Horn", "Trombone", "Tuba", "Timpani", "Violin Solo"]:
                if is_intro:
                     notes_to_play = [(0, sum([d for n, d in section]))]
                else:
                    for n, d in section:
                        val = n
                        # Climax veya Finale değilse diğerleri susar
                        if not is_climax and not is_finale and inst_name not in ["String Ensemble", "Violin Solo"]:
                             val = 0
                        notes_to_play.append((val, d))

            # --- NOTA BASMA ---
            for note_val, duration in notes_to_play:
                if note_val == 0: 
                    time += duration
                    continue
                
                final_note = note_val
                if "Violin" in inst_name: final_note += 12
                if "Dulcimer" in inst_name: final_note += 12 
                if "Tuba" in inst_name or "Trombone" in inst_name: final_note -= 12
                if "Timpani" in inst_name: final_note -= 24
                
                if inst_name == "Cello Solo": mel_data.append(final_note)
                
                t_off, v_var = get_human_touch(inst_name, duration)
                
                vol = 90
                if "Cello" in inst_name: vol = 115 
                elif "Dulcimer" in inst_name: vol = 95
                elif "Choir" in inst_name: vol = 80
                elif "Horn" in inst_name or "Trombone" in inst_name: vol = 105
                
                if inst_name == "Timpani":
                    if (is_climax or is_finale) and duration >= 1.5:
                        midi.addNote(track, channel, final_note, time, 0.5, 127)
                else:
                    midi.addNote(track, channel, final_note, time + t_off, duration * 0.85, vol + v_var)
                
                time += duration
        track += 1

    # SAVAŞ DAVULLARI (DÜZELTİLMİŞ)
    perc_track = track
    midi.addTrackName(perc_track, 0, "War Drums")
    midi.addProgramChange(perc_track, 9, 48, 0) 
    
    time = 0
    total_len = 0
    for s in song_structure:
        for n, d in s: total_len += d
        
    intro_dur = sum([d for n, d in intro_rhythm])
    
    while time < total_len:
        if time >= intro_dur: 
            if time % 3.0 == 0: 
                midi.addNote(perc_track, 9, 41, time, 0.5, 110) # DUM
                midi.addNote(perc_track, 9, 43, time, 0.5, 110) # DUM
            
            # Finale yaklaştıkça davullar hızlansın
            if time > total_len * 0.7: 
                if (time * 2) % 2 != 0 and time % 1.0 != 0: 
                     midi.addNote(perc_track, 9, 43, time, 0.25, 90) # tak tak

        time += 0.5

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    print(f"\n[+] DOSYA KAYDEDİLDİ: {filename}")
    return mel_data

# --- PDF & GRAFİK ---
def convert_midi_to_pdf_via_xml(midi_filename):
    if not MUSIC21_AVAILABLE: return
    print(f"\n[i] '{midi_filename}' için PDF hazırlanıyor...")
    
    paths = [
        '/Applications/MuseScore 4.app/Contents/MacOS/mscore',
        '/Applications/MuseScore Studio.app/Contents/MacOS/mscore'
    ]
    musescore_path = next((p for p in paths if os.path.exists(p)), None)
    if not musescore_path: return

    try:
        score = music21.converter.parse(midi_filename).quantize(quarterLengthDivisors=(4,))
        for part in score.parts:
            if "Drum" in (part.partName or ""):
                part.insert(0, instrument.Percussion())
                part.insert(0, clef.PercussionClef())
                for n in part.recurse().notes:
                     if hasattr(n, 'storedInstrument'): n.storedInstrument = None
            elif "Dulcimer" in (part.partName or ""):
                 part.insert(0, instrument.Dulcimer()) 

        xml_filename = midi_filename.replace(".mid", ".musicxml")
        score.write('musicxml', fp=xml_filename)
        pdf_output = midi_filename.replace(".mid", "_WesterosScore.pdf")
        subprocess.run([musescore_path, xml_filename, "-o", pdf_output], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        if os.path.exists(pdf_output): print(f"[+] PDF HAZIR: {pdf_output}")
    except: pass

def analyze_composition(full_mel, midi_filename):
    if not GRAPH_AVAILABLE: return
    print("\n[i] Grafik çiziliyor...")
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    def get_note_name(midi_val): return note_names[midi_val % 12]
    melody_names = [get_note_name(n) for n in full_mel if n > 0]
    melody_counts = collections.Counter(melody_names)
    
    plt.figure(figsize=(14, 6))
    plt.style.use('ggplot') 
    plt.bar(list(melody_counts.keys()), list(melody_counts.values()), color='darkred', alpha=0.8)
    plt.title('GoT (Extended Edition) - Nota Analizi', fontsize=14)
    plt.savefig(midi_filename.replace(".mid", "_Analiz.png"))
    print(f"[+] GRAFİK HAZIR.")

# --- ANA PROGRAM ---
if __name__ == "__main__":
    song = []
    song.append(intro_rhythm)
    song.append(theme_main) 
    song.append(theme_main) 
    song.append(theme_b)    
    song.append(theme_main) 
    song.append(theme_b)    # EKLEME: Coşku devam etsin
    song.append(theme_coda) # EKLEME: Epik Bitiş

    orchestra_config = {
        "melody": [
            "Cello Solo", "Violin Solo"
        ],
        "rhythm": [
            "Dulcimer", "String Ensemble" 
        ],
        "background": [
            "Choir Aahs", "French Horn", "Trombone", "Tuba", "Timpani", "War Drums"
        ]
    }
    
    output_file = "GoT_baroque.mid"
    mel = save_orchestrated_midi(song, orchestra_config, output_file)
    analyze_composition(mel, output_file)
    convert_midi_to_pdf_via_xml(output_file)