import random
import sys
import os
import subprocess 
from midiutil import MIDIFile

# --- MOTOR KONTROLÜ ---
try:
    from baroque_engine import UniversalBaroqueSolver 
except ImportError:
    print("\n[!] HATA: 'baroque_engine.py' dosyası bulunamadı.")
    sys.exit(1)

# --- MELODİK YAPI (THE GODFATHER) ---
theme_a = [59, 64, 67, 63, 64, 71, 69, 67, 64, 60, 62]
theme_b = [59, 64, 67, 63, 64, 71, 69, 67, 64, 60, 59]
chorus_high = [69, 72, 69, 68, 69, 76, 74, 72, 71, 69, 68, 69]
chorus_low  = [69, 67, 66, 64, 63, 64]
intro_outro = [64, 60, 59, 60, 64] 
solo_theme  = [71, 76, 79, 75, 76, 83, 81, 79, 76, 72, 74]

# --- ENSTRÜMANLAR ---
INSTRUMENTS = {
    "Grand Piano": 0, "Violin": 40, "String Ensemble": 48,
    "Cello": 42, "Contrabass": 43, "Flute": 73,
    "Choir Soprano": 52, "Choir Bass": 52, "Voice Oohs": 53,
    "Nylon Guitar": 24
}

# --- STEREO AYARLARI ---
MIXER_SETTINGS = {
    "Violin": {"pan": 30, "reverb": 70}, 
    "String Ensemble": {"pan": 64, "reverb": 100}, 
    "Cello": {"pan": 100, "reverb": 60}, 
    "Contrabass": {"pan": 110, "reverb": 50}, 
    "Grand Piano": {"pan": 60, "reverb": 60}, 
    "Nylon Guitar": {"pan": 80, "reverb": 50}, 
    "Flute": {"pan": 50, "reverb": 90}, 
    "Voice Oohs": {"pan": 64, "reverb": 100},
    "Choir Soprano": {"pan": 40, "reverb": 110}, 
    "Choir Bass": {"pan": 90, "reverb": 110}  
}

# --- OTOMATİK PDF DÖNÜŞTÜRÜCÜ (Music21 Yerine Subprocess) ---
def convert_midi_to_pdf(midi_filename):
    """
    MuseScore'u direkt komut satırından çağırarak PDF oluşturur.
    Music21 kütüphanesindeki hataları bypass eder. Yoksa PDF oluşmuyor.
    """
    print(f"\n[i] '{midi_filename}' otomatik olarak PDF'e dönüştürülüyor...")
    
    # MuseScore Yolu (MacOS için)
    musescore_path = '/Applications/MuseScore 4.app/Contents/MacOS/mscore'
    
    # Eğer MuseScore 4 yoksa Studio'yu dene
    if not os.path.exists(musescore_path):
        musescore_path = '/Applications/MuseScore Studio.app/Contents/MacOS/mscore'
    
    if not os.path.exists(musescore_path):
        print("[!] MuseScore uygulaması bulunamadı. PDF oluşturulamıyor.")
        return

    # Çıktı dosyası ismi
    pdf_output = midi_filename.replace(".mid", ".pdf")
    
    # Komut: mscore input.mid -o output.pdf
    try:
        command = [musescore_path, midi_filename, "-o", pdf_output]
        
        # Komutu çalıştır ama gereksiz QML hatalarını ekrana basma
        process = subprocess.run(command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        if process.returncode == 0 or os.path.exists(pdf_output):
            print(f"[+] BAŞARILI: PDF Notası Oluşturuldu -> {pdf_output}")
        else:
            print("[!] PDF oluşturma işlemi tamamlanamadı (MuseScore hatası).")
            
    except Exception as e:
        print(f"[!] Bir hata oluştu: {e}")

# --- ANALİZ GRAFİĞİ (Matplotlib) ---
def analyze_composition(full_cf, full_cp, midi_filename):
    try:
        import matplotlib.pyplot as plt
        import collections
        
        print("\n[i] Analiz grafiği oluşturuluyor...")
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        def get_note_name(midi_val): return note_names[midi_val % 12]
        
        melody_names = [get_note_name(n) for n in full_cp]
        melody_counts = collections.Counter(melody_names)
        
        plt.figure(figsize=(14, 9))
        plt.style.use('ggplot') 
        
        plt.subplot(2, 1, 1)
        plt.bar(list(melody_counts.keys()), list(melody_counts.values()), color='firebrick', alpha=0.7)
        plt.title('AI Nota Tercihleri', fontsize=14)
        
        plt.subplot(2, 1, 2)
        plt.plot(full_cp, label='Melodi', color='royalblue', linewidth=2)
        plt.plot(full_cf, label='Bas', color='gray', linestyle='--', alpha=0.7)
        plt.title('Melodik Hareket', fontsize=14)
        plt.legend()
        plt.tight_layout()
        
        png_name = midi_filename.replace(".mid", "_Analiz.png")
        plt.savefig(png_name)
        print(f"[+] GRAFİK KAYDEDİLDİ: {png_name}")
        
    except ImportError:
        print("[!] Matplotlib yüklü değil, grafik çizilemedi.")

# --- YARDIMCI FONKSİYONLAR ---
def get_human_touch(inst_name, measure_len, base_velocity):
    timing_offset = random.uniform(-0.01, 0.01) 
    duration_factor = 0.95 
    velocity = base_velocity + random.randint(-5, 5)
    if inst_name in ["Violin", "String Ensemble", "Cello", "Contrabass", "Choir Soprano", "Choir Bass", "Voice Oohs", "Flute"]:
        duration_factor = random.uniform(1.05, 1.10) 
        timing_offset = random.uniform(0.02, 0.05)   
    elif inst_name in ["Grand Piano", "Nylon Guitar"]:
        duration_factor = 0.90 
        timing_offset = random.uniform(-0.015, 0.015)
    return timing_offset, duration_factor, velocity

def save_orchestrated_midi(full_cf, full_cp, arrangement, filename, solo_range):
    num_tracks = len(arrangement["melody_instruments"]) + len(arrangement["bass_instruments"])
    midi = MIDIFile(num_tracks) 
    START_BPM = 105
    track_idx = 0
    channel_cursor = 0 
    solo_start, solo_end = solo_range

    all_instruments = arrangement["melody_instruments"] + arrangement["bass_instruments"]
    melody_set = set(arrangement["melody_instruments"])

    for inst_name in all_instruments:
        if channel_cursor == 9: channel_cursor += 1
        program_num = INSTRUMENTS.get(inst_name, 0)
        midi.addTrackName(track_idx, 0, inst_name)
        midi.addProgramChange(track_idx, channel_cursor, 0, program_num)
        midi.addTempo(track_idx, 0, START_BPM)
        
        settings = MIXER_SETTINGS.get(inst_name, {"pan": 64, "reverb": 40})
        midi.addControllerEvent(track_idx, channel_cursor, 0, 10, settings["pan"])
        midi.addControllerEvent(track_idx, channel_cursor, 0, 91, settings["reverb"])

        time_cursor = 0
        note_list = full_cp if inst_name in melody_set else full_cf
        
        for i, note in enumerate(note_list):
            if track_idx == 0: # Ritardando
                measures_left = len(full_cp) - i
                if measures_left <= 5:
                    drop_amount = (6 - measures_left) * 10 
                    new_bpm = max(60, START_BPM - drop_amount)
                    midi.addTempo(track_idx, time_cursor, new_bpm)

            is_solo_section = (solo_start <= i < solo_end)
            if inst_name in melody_set and is_solo_section and inst_name != "Flute":
                time_cursor += 3.0
                continue 

            play_note = note
            if inst_name == "Flute": play_note += 12
            if inst_name in ["Cello", "Contrabass", "Choir Bass"]: play_note -= 12 

            base_vol = 95
            if inst_name == "Flute": base_vol = 105 if is_solo_section else 90
            elif inst_name == "Grand Piano": base_vol = 100
            elif inst_name == "Choir Soprano": base_vol = 65
            elif inst_name == "Choir Bass": base_vol = 60
            
            t_off, d_fac, vol = get_human_touch(inst_name, 3.0, base_vol)
            
            if inst_name == "Grand Piano" and inst_name not in melody_set:
                midi.addNote(track_idx, channel_cursor, play_note - 12, time_cursor + t_off, 0.8, vol + 20)
                cp_note = full_cp[i] if i < len(full_cp) else play_note
                arp_speed = 0.05 
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + 1 + t_off, 0.7, vol - 10)
                midi.addNote(track_idx, channel_cursor, cp_note - 12, time_cursor + 1 + t_off + arp_speed, 0.7, vol - 15)
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + 2 + t_off, 0.7, vol - 10)
                midi.addNote(track_idx, channel_cursor, cp_note - 12, time_cursor + 2 + t_off + arp_speed, 0.7, vol - 15)
            elif inst_name == "Nylon Guitar" and inst_name not in melody_set:
                midi.addNote(track_idx, channel_cursor, play_note - 12, time_cursor + t_off, 0.8, vol - 10)
                cp_note = full_cp[i] if i < len(full_cp) else play_note
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + 1 + t_off, 0.8, vol - 20)
                midi.addNote(track_idx, channel_cursor, cp_note - 12, time_cursor + 2 + t_off, 0.8, vol - 20)
            else:
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + t_off, 3.0 * d_fac, vol)
            time_cursor += 3.0 
        track_idx += 1
        channel_cursor += 1 

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    print(f"\n[+] DOSYA KAYDEDİLDİ: {filename}")

def solve_atomically(segment):
    final_cf = [] 
    final_cp = [] 
    for note in segment:
        chunk = [note]
        solver = UniversalBaroqueSolver(chunk, key_root_name='E', mode='minor')
        solver.target_solutions = 1
        try:
            result = solver.solve()
            if result:
                final_cf.extend(chunk)
                final_cp.extend(result['melody'])
            else:
                final_cf.extend(chunk)
                final_cp.extend(chunk)
        except Exception:
             final_cf.extend(chunk)
             final_cp.extend(chunk)
    return final_cf, final_cp

def generate_full_song_structure():
    song_structure = []
    song_structure.append(intro_outro) 
    song_structure.append(theme_a)
    song_structure.append(theme_b)
    song_structure.append(chorus_high)
    song_structure.append(chorus_low)
    song_structure.append(intro_outro)
    solo_section_content = solo_theme + solo_theme 
    song_structure.append(solo_section_content) 
    song_structure.append(theme_a)
    song_structure.append(theme_b)
    song_structure.append(intro_outro)
    song_structure.append([64, 64, 64, 64]) 

    full_cf = []
    full_cp = []
    solo_start_index = 0
    solo_end_index = 0
    current_note_count = 0
    
    print(f"\n[>] Godfather Waltz (Automated PDF Edition) Hazırlanıyor...")
    
    for i, section in enumerate(song_structure):
        is_this_solo = (section == solo_section_content)
        if is_this_solo:
            solo_start_index = current_note_count
            solo_end_index = current_note_count + len(section)
            full_cf.extend(section)
            full_cp.extend(section)
        else:
            seg_cf, seg_cp = solve_atomically(section)
            full_cf.extend(seg_cf)
            full_cp.extend(seg_cp)
        current_note_count += len(section)

    return full_cf, full_cp, (solo_start_index, solo_end_index)

if __name__ == "__main__":
    cf, cp, solo_range = generate_full_song_structure()
    
    if cf:
        orchestra_config = {
            "melody_instruments": ["Violin", "Flute", "Choir Soprano"], 
            "bass_instruments": [
                "Grand Piano", "String Ensemble", "Choir Bass",
                "Voice Oohs", "Cello", "Contrabass", "Nylon Guitar"
            ] 
        }
        
        output_file = "Godfather_Auto.mid"
        
        # 1. MIDI Kaydet
        save_orchestrated_midi(cf, cp, orchestra_config, output_file, solo_range)
        
        # 2. Grafik Kaydet
        analyze_composition(cf, cp, output_file)
        
        # 3. PDF'i Otomatik Oluştur (ZORLA)
        convert_midi_to_pdf(output_file)