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
    print("[!] UYARI: Matplotlib yok.")

try:
    import music21
    # Clef ve Note modülleri
    from music21 import stream, converter, instrument, clef, note
    MUSIC21_AVAILABLE = True
    print("[OK] Music21 yüklü.")
except ImportError:
    MUSIC21_AVAILABLE = False
    print("[!!!] KRİTİK: 'music21' yok.")

print("-----------------------\n")

# --- MELODİK YAPI ---
theme_a = [64, 67, 66, 64, 63, 64, 66, 67, 69, 71, 74, 71, 69, 67, 66, 64]
theme_b = [71, 74, 76, 74, 72, 71, 69, 67, 66, 64, 63, 64, 66, 69, 71, 76]
bridge = [76, 75, 76, 79, 78, 79, 81, 79, 76, 72, 69, 67, 64, 60, 59, 52]
intro_outro = [52, 59, 64, 67, 64, 59, 52]
solo_theme = [76, 79, 78, 76, 74, 76, 78, 79, 81, 83, 84, 83, 81, 79, 78, 76]

# --- ENSTRÜMANLAR ---
INSTRUMENTS = {
    "Violin": 40, "Viola": 41, "Cello": 42, "Contrabass": 43, 
    "String Ensemble": 48, "Orchestral Harp": 46,
    "Flute": 73, "Piccolo": 72, "Oboe": 68, "Clarinet": 71, "Bassoon": 70,
    "Trumpet": 56, "French Horn": 60, "Trombone": 57, "Tuba": 58,
    "Timpani": 47, "Percussion Kit": 0, "Choir Aahs": 52, "Pad (Ambient)": 89
}

# --- MİKSER ---
MIXER_SETTINGS = {
    "Violin": {"pan": 40, "reverb": 70},
    "Viola": {"pan": 50, "reverb": 70},
    "Flute": {"pan": 45, "reverb": 80},
    "Clarinet": {"pan": 55, "reverb": 70},
    "French Horn": {"pan": 30, "reverb": 90},
    "Orchestral Harp": {"pan": 40, "reverb": 60},
    "String Ensemble": {"pan": 64, "reverb": 100},
    "Oboe": {"pan": 64, "reverb": 70},
    "Piccolo": {"pan": 60, "reverb": 80},
    "Choir Aahs": {"pan": 64, "reverb": 110},
    "Pad (Ambient)": {"pan": 64, "reverb": 120},
    "Timpani": {"pan": 64, "reverb": 100},
    "Percussion Kit": {"pan": 64, "reverb": 50},
    "Cello": {"pan": 80, "reverb": 60},
    "Contrabass": {"pan": 90, "reverb": 50},
    "Bassoon": {"pan": 75, "reverb": 70},
    "Trombone": {"pan": 85, "reverb": 80},
    "Trumpet": {"pan": 75, "reverb": 80},
    "Tuba": {"pan": 90, "reverb": 80}
}

# --- YARDIMCI FONKSİYONLAR ---
def get_human_touch(inst_name, duration):
    timing = random.uniform(-0.02, 0.02)
    vel_var = random.randint(-5, 5)
    return timing, vel_var

# --- SEÇİLMİŞ ENSTRÜMANLI PDF ---
def convert_midi_to_pdf_selective(midi_filename):
    if not MUSIC21_AVAILABLE:
        return

    print(f"\n[i] '{midi_filename}' için SEÇİLMİŞ PARTİSYON PDF'i hazırlanıyor...")
    
    # MuseScore Yolu
    paths = [
        '/Applications/MuseScore 4.app/Contents/MacOS/mscore',
        '/Applications/MuseScore Studio.app/Contents/MacOS/mscore',
        '/Applications/MuseScore Studio 4.app/Contents/MacOS/mscore'
    ]
    musescore_path = None
    for p in paths:
        if os.path.exists(p):
            musescore_path = p
            break
            
    if not musescore_path:
        print("[!] MuseScore bulunamadı.")
        return

    try:
        # MIDI Oku
        score = music21.converter.parse(midi_filename)
        
        # --- TAMİPERKÜSYON HATASI DÜZELTME ---
        for part in score.parts:
            p_name = part.partName if part.partName else ""
            is_percussion = "Percussion" in p_name
            if not is_percussion:
                try:
                    for n in part.recurse().notes:
                        if isinstance(n, music21.note.Unpitched):
                            is_percussion = True
                            break
                except: pass
            
            if is_percussion:
                # Partisyona temiz kimlik ver
                part.insert(0, instrument.Percussion())
                part.insert(0, clef.PercussionClef())
                # Hatalı etiketleri temizle
                for n in part.recurse().notes:
                    if hasattr(n, 'storedInstrument'):
                        n.storedInstrument = None
        # -------------------------------------------------------------

        # ÖNEMLİ ENSTRÜMANLARI SEÇ
        important_parts = [
            "Violin", "Oboe", "Flute", "French Horn", "String Ensemble",
            "Cello", "Contrabass", "Timpani", "Percussion", "Harp"
        ]
        
        new_score = stream.Score()
        
        for part in score.parts:
            p_name = part.partName if part.partName else ""
            # Listede varsa ekle
            if any(imp in p_name for imp in important_parts):
                new_score.insert(0, part)
        
        if len(new_score.parts) == 0:
            new_score = score # Hiçbiri yoksa hepsini bas
            
        # 3. XML Kaydet
        xml_filename = midi_filename.replace(".mid", "_Selected.musicxml")
        new_score.write('musicxml', fp=xml_filename)
        
        # 4. PDF Oluştur (Orkestra Partisyonu fazlaysa kaydetmez)
        pdf_output = midi_filename.replace(".mid", "_ConductorScore.pdf")
        command = [musescore_path, xml_filename, "-o", pdf_output]
        
        subprocess.run(command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        if os.path.exists(pdf_output):
            print(f"[+] BAŞARILI: Seçilmiş Partisyon PDF Hazır -> {pdf_output}")
            try: os.remove(xml_filename)
            except: pass
        else:
            print("[!] PDF oluşturulamadı.")
            
    except Exception as e:
        print(f"[!] PDF HATASI: {e}")

def analyze_composition(full_mel, full_bas, midi_filename):
    if not GRAPH_AVAILABLE: return
    print("\n[i] Grafik çiziliyor...")
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    def get_note_name(midi_val): return note_names[midi_val % 12]
    melody_names = [get_note_name(n) for n in full_mel]
    melody_counts = collections.Counter(melody_names)
    
    plt.figure(figsize=(14, 9))
    plt.style.use('dark_background') 
    plt.subplot(2, 1, 1)
    plt.bar(list(melody_counts.keys()), list(melody_counts.values()), color='purple', alpha=0.8)
    plt.title('Across the Stars - Nota Analizi', fontsize=14, color='white')
    
    plt.subplot(2, 1, 2)
    plt.plot(full_mel, label='Melodi', color='cyan', linewidth=2)
    plt.plot(full_bas, label='Bas', color='gray', linestyle='--')
    plt.legend()
    plt.savefig(midi_filename.replace(".mid", "_Analiz.png"))
    print(f"[+] GRAFİK HAZIR.")

def generate_safe_harmony(segment):
    harmony = []
    for n in segment:
        harmony.append(n - 12) 
    return harmony, segment

# --- MIDI OLUŞTURMA ---
def save_orchestrated_midi(full_mel, full_bas, arrangement, filename, solo_range):
    num_tracks = len(arrangement["melody"] + arrangement["bass"]) + 1 
    midi = MIDIFile(num_tracks) 
    START_BPM = 85 
    track_idx = 0       
    channel_cursor = 0  
    
    all_insts = arrangement["melody"] + arrangement["bass"]
    
    for inst_name in all_insts:
        if channel_cursor == 9: channel_cursor += 1
        if channel_cursor > 15: channel_cursor = 0 
        
        midi.addTrackName(track_idx, 0, inst_name)
        midi.addProgramChange(track_idx, channel_cursor, 0, INSTRUMENTS.get(inst_name, 0))
        midi.addTempo(track_idx, 0, START_BPM)
        
        settings = MIXER_SETTINGS.get(inst_name, {"pan": 64, "reverb": 50})
        midi.addControllerEvent(track_idx, channel_cursor, 0, 10, settings["pan"])
        midi.addControllerEvent(track_idx, channel_cursor, 0, 91, settings["reverb"])
        
        time = 0
        note_list = full_mel if inst_name in arrangement["melody"] else full_bas
        if not note_list: note_list = full_mel

        for i, note in enumerate(note_list):
            duration = 3.0 
            is_solo = (solo_range[0] <= i < solo_range[1])
            if inst_name in arrangement["melody"] and is_solo and inst_name not in ["Oboe", "Violin", "Flute"]:
                time += duration
                continue

            play_note = note
            if inst_name in ["Piccolo", "Flute", "Violin", "Oboe", "Clarinet", "Trumpet"]: play_note += 12
            if inst_name in ["Cello", "Trombone", "Bassoon", "Tuba", "Contrabass", "Choir Aahs"]: play_note -= 12
            if inst_name == "Timpani": play_note -= 24

            vol = 90
            if inst_name in ["French Horn", "Trombone", "Trumpet"]: vol = 105 
            if inst_name == "Timpani": vol = 115
            if inst_name == "Oboe": vol = 100 
            if inst_name == "Pad (Ambient)": vol = 60 
            
            t_off, v_var = get_human_touch(inst_name, duration)
            
            if inst_name == "Orchestral Harp":
                midi.addNote(track_idx, channel_cursor, play_note, time + t_off, 2.5, vol)
                midi.addNote(track_idx, channel_cursor, play_note+7, time + 0.2 + t_off, 2.5, vol-10)
                midi.addNote(track_idx, channel_cursor, play_note+12, time + 0.4 + t_off, 2.5, vol-15)
            elif inst_name == "Timpani":
                midi.addNote(track_idx, channel_cursor, play_note, time + t_off, 0.5, vol)
            elif inst_name == "String Ensemble" or inst_name == "Pad (Ambient)":
                midi.addNote(track_idx, channel_cursor, play_note, time, duration, vol)
            elif inst_name in ["Trumpet", "Trombone", "French Horn", "Tuba"]:
                midi.addNote(track_idx, channel_cursor, play_note, time + t_off, duration * 0.9, vol)
            else:
                midi.addNote(track_idx, channel_cursor, play_note, time + t_off, duration * 0.95, vol + v_var)
            time += duration
        
        track_idx += 1
        channel_cursor += 1

    # Perküsyon
    perc_track = track_idx 
    midi.addTrackName(perc_track, 0, "Percussion")
    midi.addProgramChange(perc_track, 9, 0, 0) 
    
    time = 0
    total_len = len(full_mel) * 3.0
    while time < total_len:
        midi.addNote(perc_track, 9, 36, time, 1.0, 110) 
        if random.random() < 0.1: 
            midi.addNote(perc_track, 9, 54, time, 4.0, 100) 
        midi.addNote(perc_track, 9, 41, time + 1.0, 0.5, 80)
        midi.addNote(perc_track, 9, 43, time + 2.0, 0.5, 85)
        if random.random() < 0.3:
            midi.addNote(perc_track, 9, 81, time + 2.5, 0.5, 70)
        time += 3.0

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    print(f"\n[+] DOSYA KAYDEDİLDİ: {filename}")
    return all_insts

# --- ŞARKI TRAFİĞİ ---
def generate_full_song_structure():
    structure = []
    structure.append(intro_outro)
    structure.append(theme_a)
    structure.append(theme_b)
    structure.append(theme_a)
    
    solo_sect = solo_theme + solo_theme
    structure.append(solo_sect)
    
    structure.append(bridge) 
    structure.append(theme_b)
    structure.append(theme_a)
    structure.append(intro_outro)
    structure.append([64, 64, 64])

    full_mel = []
    full_bas = []
    
    solo_start = 0
    solo_end = 0
    current = 0
    
    print(f"\n[>] Across the Stars (Full Orchestra) Hazırlanıyor...")
    
    for section in structure:
        if section == solo_sect:
            solo_start = current
            solo_end = current + len(section)
        
        bas_part, mel_part = generate_safe_harmony(section)
        full_mel.extend(mel_part)
        full_bas.extend(bas_part)
        current += len(section)
        
    return full_mel, full_bas, (solo_start, solo_end)

if __name__ == "__main__":
    mel, bas, solo_range = generate_full_song_structure()
    
    if mel:
        orchestra_config = {
            "melody": [
                "Violin", "Oboe", "Flute", "Clarinet", "Piccolo", 
                "French Horn", "String Ensemble", "Orchestral Harp"
            ],
            "bass": [
                "Cello", "Contrabass", "Bassoon", "Tuba", "Trombone", 
                "Choir Aahs", "Timpani", "Pad (Ambient)", "Viola"
            ]
        }
        
        output_file = "Love_Pledge_bareque.mid"
        save_orchestrated_midi(mel, bas, orchestra_config, output_file, solo_range)
        analyze_composition(mel, bas, output_file)
        
        # Conductor PDF
        convert_midi_to_pdf_selective(output_file)