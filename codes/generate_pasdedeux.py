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
    from music21 import instrument, clef, note, stream
    MUSIC21_AVAILABLE = True
    print("[OK] Music21 yüklü.")
except ImportError:
    MUSIC21_AVAILABLE = False

print("-----------------------\n")

# --- 1. MELODİK YAPI ---
theme_a = [(79, 1.5), (78, 0.5), (76, 1.0), (74, 1.0), (72, 1.5), (71, 0.5), (69, 1.0), (67, 1.0), (66, 1.5), (64, 0.5), (62, 1.0), (60, 1.0), (59, 2.0), (62, 1.0), (67, 1.0)]
theme_b = [(74, 2.0), (74, 1.0), (76, 0.5), (77, 0.5), (79, 2.0), (79, 1.0), (81, 0.5), (83, 0.5), (84, 1.5), (83, 0.5), (81, 1.0), (79, 1.0), (78, 2.0), (74, 2.0)]
heaven_climax = [(91, 1.0), (89, 1.0), (88, 1.0), (86, 1.0), (84, 1.0), (83, 1.0), (81, 1.0), (79, 1.0), (78, 1.0), (76, 1.0), (74, 1.0), (72, 1.0), (71, 1.0), (69, 1.0), (67, 1.0), (66, 1.0), (67, 4.0)]
coda = [(67, 0.5), (71, 0.5), (74, 0.5), (79, 0.5), (83, 0.5), (86, 0.5), (91, 1.0), (67, 0.5), (67, 0.5), (67, 0.5), (67, 0.5), (67, 4.0)]
intro_harp = [(67, 4.0), (60, 4.0), (55, 4.0), (67, 4.0)]

# --- 2. ENSTRÜMAN LİSTESİ ---
INSTRUMENTS = {
    "Orchestral Harp": 46, "Violin Solo": 40, "Cello Solo": 42, "Grand Piano": 0,   
    "Flute": 73, "Oboe": 68, "Clarinet": 71, "Bassoon": 70, "French Horn": 60, 
    "Trombone": 57, "Tuba": 58, "Trumpet": 56, "String Ensemble": 48, 
    "Contrabass": 43, "Harpsichord": 6
}

# --- 3. MİKSER ---
MIXER_SETTINGS = {
    "Orchestral Harp": {"pan": 40, "reverb": 100}, "Violin Solo": {"pan": 60, "reverb": 90}, 
    "Cello Solo": {"pan": 70, "reverb": 90}, "Flute": {"pan": 45, "reverb": 80},
    "French Horn": {"pan": 30, "reverb": 70}, "Tuba": {"pan": 90, "reverb": 60}
}

# --- 4. YARDIMCI FONKSİYONLAR ---
def get_human_touch(inst_name, duration):
    timing = random.uniform(-0.01, 0.01) 
    vel_var = random.randint(-3, 3)
    return timing, vel_var

def generate_heavenly_arpeggio(root, duration):
    notes = []
    if root == 0: return [(0, duration)]
    intervals = [0, 4, 7, 12, 16, 19, 24, 28, 31, 36] 
    steps = int(duration / 0.25)
    for i in range(steps):
        idx = i % len(intervals)
        notes.append((root + intervals[idx] - 12, 0.25))
    return notes

# --- 5. MIDI OLUŞTURMA ---
def save_orchestrated_midi(song_structure, arrangement, filename):
    midi = MIDIFile(len(arrangement["melody"] + arrangement["bass"] + arrangement["harmony"]) + 1)
    track = 0
    START_BPM = 58 
    
    all_insts = arrangement["melody"] + arrangement["bass"] + arrangement["harmony"]
    
    mel_data = [] # Analiz için notalar
    
    for inst_name in all_insts:
        channel = track if track < 16 else 15 
        midi.addTrackName(track, 0, inst_name)
        midi.addProgramChange(track, channel, 0, INSTRUMENTS.get(inst_name, 0))
        midi.addTempo(track, 0, START_BPM)
        
        time = 0
        for section in song_structure:
            is_heaven = (section == heaven_climax)
            is_intro = (section == intro_harp)
            is_theme_a = (section == theme_a)
            
            should_play = True
            if is_intro and inst_name != "Orchestral Harp": should_play = False
            elif is_theme_a and inst_name in ["Trumpet", "Trombone", "Tuba"]: should_play = False

            if not should_play:
                duration_total = sum([d for n,d in section])
                time += duration_total
                continue

            if "Harp" in inst_name:
                for n, d in section:
                    if is_heaven: 
                        arpeggio = generate_heavenly_arpeggio(n, d)
                        for note_val, dur in arpeggio:
                            midi.addNote(track, channel, note_val, time, dur, 100)
                            mel_data.append(note_val) # Analize ekle
                            time += dur
                    else: 
                        steps = int(d/0.5)
                        for i in range(steps): 
                            val = n + [0,4,7,12][i%4] - 12
                            midi.addNote(track, channel, val, time, 0.5, 90)
                            mel_data.append(val)
                            time += 0.5
            else:
                for note_val, duration in section:
                    if note_val == 0: 
                        time += duration
                        continue
                    
                    final_note = note_val
                    if "Flute" in inst_name: final_note += 12
                    if "Cello" in inst_name: final_note -= 12
                    if "Bass" in inst_name or "Tuba" in inst_name: final_note -= 24
                    
                    mel_data.append(final_note) # Analize ekle
                    
                    t_off, v_var = get_human_touch(inst_name, duration)
                    vol = 80
                    if is_heaven: vol = 110 
                    
                    midi.addNote(track, channel, final_note, time + t_off, duration * 1.05, vol + v_var)
                    time += duration
        track += 1

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    print(f"\n[+] DOSYA KAYDEDİLDİ: {filename}")
    return mel_data

# --- PDF & GRAFİK (GÜNCELLENMİŞ) ---
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
            part.insert(0, instrument.fromString(part.partName if part.partName else "Piano"))
            for n in part.recurse().notes:
                if hasattr(n, 'storedInstrument'): n.storedInstrument = None

        xml_filename = midi_filename.replace(".mid", ".musicxml")
        score.write('musicxml', fp=xml_filename)
        pdf_output = midi_filename.replace(".mid", "_AnalyticScore.pdf")
        subprocess.run([musescore_path, xml_filename, "-o", pdf_output], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        if os.path.exists(pdf_output): print(f"[+] PDF HAZIR: {pdf_output}")
    except: pass

# --- [YENİ] DETAYLI ANALİZ GRAFİĞİ ---
def analyze_composition(full_mel, midi_filename):
    if not GRAPH_AVAILABLE: return
    print("\n[i] Detaylı analiz grafikleri oluşturuluyor...")
    
    # Nota isimleri (0=C, 1=C#...)
    note_names_map = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    def get_note_name(midi_val): return note_names_map[midi_val % 12]
    
    # 1. Veri Hazırla
    melody_names = [get_note_name(n) for n in full_mel if n > 0]
    melody_counts = collections.Counter(melody_names)
    
    # Grafiği Çiz (2 Panel: Zaman Serisi + Pasta Grafik)
    plt.figure(figsize=(16, 8))
    
    # --- Panel 1: Melodik Hareket (Çizgi Grafik) ---
    plt.subplot(1, 2, 1)
    # Performans için her 10 notadan birini al (Downsample)
    plt.plot(full_mel[::10], color='royalblue', alpha=0.7, linewidth=1.5)
    plt.title('Melodik Yükseliş ve Alçalış (Time Series)', fontsize=14)
    plt.xlabel('Zaman (Nota Sırası)')
    plt.ylabel('Pitch (MIDI Değeri)')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # --- Panel 2: Nota Dağılımı (Pasta Grafik) ---
    plt.subplot(1, 2, 2)
    # En çok kullanılan 8 notayı al, gerisine "Diğer" de
    common = melody_counts.most_common(8)
    labels = [x[0] for x in common]
    sizes = [x[1] for x in common]
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
            colors=plt.cm.Paired.colors)
    plt.title('Nota Kullanım Oranları (Pie Chart)', fontsize=14)
    
    # Kaydet
    plt.tight_layout()
    plt.savefig(midi_filename.replace(".mid", "_Analiz.png"), dpi=150)
    print(f"[+] GRAFİK HAZIR: {midi_filename.replace('.mid', '_Analiz.png')}")

# --- ANA PROGRAM ---
if __name__ == "__main__":
    song = [intro_harp, theme_a, theme_a, theme_b, theme_a, heaven_climax, theme_b, theme_a, coda]
    config = {
        "melody": ["Orchestral Harp", "Violin Solo", "Cello Solo", "Flute", "Oboe"],
        "harmony": ["Clarinet", "French Horn", "Trumpet", "Trombone"],
        "bass": ["Bassoon", "Tuba", "Contrabass"]
    }
    
    output_file = "PasDeDeux_Analytic.mid"
    all_notes = save_orchestrated_midi(song, config, output_file)
    analyze_composition(all_notes, output_file)
    convert_midi_to_pdf_via_xml(output_file)