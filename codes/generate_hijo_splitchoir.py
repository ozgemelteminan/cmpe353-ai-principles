import random
import sys
import os
import subprocess
import collections
from midiutil import MIDIFile

# --- GEREKLİ KÜTÜPHANE KONTROLLERİ ---
try:
    from baroque_engine import UniversalBaroqueSolver 
except ImportError:
    print("\n[!] HATA: 'baroque_engine.py' dosyası bulunamadı.")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False
    print("[!] Matplotlib yüklü değil, grafik çizilemeyecek.")

# --- MELODİK YAPI TASLARI ---
verse_theme_a = [71, 72, 71, 69, 67, 66, 64] 
verse_theme_b = [66, 69, 67, 66, 64]          
pre_chorus = [64, 66, 67, 69, 71, 72, 74, 71] 
chorus_high = [76, 75, 76, 75, 76, 72, 69, 67, 69]
chorus_low  = [72, 71, 72, 71, 72, 69, 66, 64]      
intro_outro = [64, 66, 67, 69, 71, 64] 
solo_theme  = [76, 79, 76, 74, 76, 79, 81, 79, 76, 74, 72] 

# --- ENSTRÜMAN LİSTESİ ---
INSTRUMENTS = {
    "Grand Piano": 0,
    "Violin": 40,
    "String Ensemble": 48,
    "Cello": 42,
    "Contrabass": 43,
    "Flute": 73,
    "Choir Aahs": 52,     
    "Choir Soprano": 52,  
    "Choir Bass": 52,     
    "Voice Oohs": 53,
    "Nylon Guitar": 24
}

# --- STEREO AYARLARI ---
MIXER_SETTINGS = {
    "Violin":            {"pan": 30,  "reverb": 60}, 
    "String Ensemble":   {"pan": 64,  "reverb": 90}, 
    "Cello":             {"pan": 100, "reverb": 50}, 
    "Contrabass":        {"pan": 110, "reverb": 40}, 
    "Grand Piano":       {"pan": 60,  "reverb": 50}, 
    "Nylon Guitar":      {"pan": 80,  "reverb": 40}, 
    "Flute":             {"pan": 50,  "reverb": 80}, 
    "Voice Oohs":        {"pan": 64,  "reverb": 90},
    
    # KORO AYRIŞTIRMA (PANNING)
    "Choir Soprano":     {"pan": 40,  "reverb": 100}, # Soldan gelir
    "Choir Bass":        {"pan": 90,  "reverb": 100}  # Sağdan gelir
}

# --- OTOMATİK PDF DÖNÜŞTÜRÜCÜ ---
def convert_midi_to_pdf(midi_filename):
    print(f"\n[i] '{midi_filename}' otomatik olarak PDF'e dönüştürülüyor...")
    
    # MuseScore Yolu (MacOS için)
    musescore_path = '/Applications/MuseScore 4.app/Contents/MacOS/mscore'
    
    # Eğer MuseScore 4 yoksa Studio'yu dene
    if not os.path.exists(musescore_path):
        musescore_path = '/Applications/MuseScore Studio.app/Contents/MacOS/mscore'
    
    if not os.path.exists(musescore_path):
        print("[!] MuseScore uygulaması bulunamadı. PDF oluşturulamıyor.")
        return

    pdf_output = midi_filename.replace(".mid", ".pdf")
    
    try:
        command = [musescore_path, midi_filename, "-o", pdf_output]
        process = subprocess.run(command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        if process.returncode == 0 or os.path.exists(pdf_output):
            print(f"[+] BAŞARILI: PDF Notası Oluşturuldu -> {pdf_output}")
        else:
            print("[!] PDF oluşturma işlemi tamamlanamadı.")
    except Exception as e:
        print(f"[!] Bir hata oluştu: {e}")

# --- ANALİZ GRAFİĞİ ---
def analyze_composition(full_cf, full_cp, midi_filename):
    if not GRAPH_AVAILABLE:
        return

    print("\n[i] Analiz grafiği oluşturuluyor...")
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    def get_note_name(midi_val): return note_names[midi_val % 12]
    
    melody_names = [get_note_name(n) for n in full_cp]
    melody_counts = collections.Counter(melody_names)
    
    plt.figure(figsize=(14, 9))
    plt.style.use('ggplot') 
    
    # Grafik 1: Nota Dağılımı
    plt.subplot(2, 1, 1)
    plt.bar(list(melody_counts.keys()), list(melody_counts.values()), color='firebrick', alpha=0.7)
    plt.title('Hijo de la Luna - Nota Tercih Dağılımı', fontsize=14)
    plt.ylabel('Kullanım Sayısı')
    
    # Grafik 2: Melodik Hareket
    plt.subplot(2, 1, 2)
    plt.plot(full_cp, label='Melodi (Soprano/Flüt)', color='royalblue', linewidth=2)
    plt.plot(full_cf, label='Bas (Piyano/Cello)', color='gray', linestyle='--', alpha=0.7)
    plt.title('Melodik Hareket ve Tansiyon', fontsize=14)
    plt.legend()
    plt.tight_layout()
    
    png_name = midi_filename.replace(".mid", "_Analiz.png")
    plt.savefig(png_name)
    print(f"[+] GRAFİK KAYDEDİLDİ: {png_name}")

def get_human_touch(inst_name, measure_len, base_velocity):
    timing_offset = random.uniform(-0.01, 0.01) 
    duration_factor = 0.95 
    velocity = base_velocity + random.randint(-5, 5)

    # Legato (Yaylılar ve Koro)
    if inst_name in ["Violin", "String Ensemble", "Cello", "Contrabass", "Choir Aahs", "Choir Soprano", "Choir Bass", "Voice Oohs", "Flute"]:
        duration_factor = random.uniform(1.05, 1.10) 
        timing_offset = random.uniform(0.02, 0.05)   
    
    elif inst_name in ["Grand Piano", "Nylon Guitar"]:
        duration_factor = 0.90 
        timing_offset = random.uniform(-0.015, 0.015)

    return timing_offset, duration_factor, velocity

def save_orchestrated_waltz_midi(full_cf, full_cp, arrangement, filename, solo_range):
    num_tracks = len(arrangement["melody_instruments"]) + len(arrangement["bass_instruments"])
    midi = MIDIFile(num_tracks) 
    
    BPM = 148
    MEASURE_LEN = 3.0 
    
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
        midi.addTempo(track_idx, 0, BPM)
        
        settings = MIXER_SETTINGS.get(inst_name, {"pan": 64, "reverb": 40})
        midi.addControllerEvent(track_idx, channel_cursor, 0, 10, settings["pan"])
        midi.addControllerEvent(track_idx, channel_cursor, 0, 91, settings["reverb"])

        time_cursor = 0
        note_list = full_cp if inst_name in melody_set else full_cf
        
        for i, note in enumerate(note_list):
            is_solo_section = (solo_start <= i < solo_end)
            if inst_name in melody_set and is_solo_section and inst_name != "Flute":
                time_cursor += MEASURE_LEN
                continue 

            play_note = note
            
            # --- ÖZEL AYARLAR ---
            if inst_name == "Flute": play_note += 12
            if inst_name in ["Cello", "Contrabass", "Choir Bass"]: play_note -= 12 

            base_vol = 95
            if inst_name == "Flute": base_vol = 100 if is_solo_section else 90
            elif inst_name == "Grand Piano": base_vol = 100
            elif inst_name == "Choir Soprano": base_vol = 65
            elif inst_name == "Choir Bass": base_vol = 60
            
            t_off, d_fac, vol = get_human_touch(inst_name, MEASURE_LEN, base_vol)
            
            if inst_name == "Grand Piano" and inst_name not in melody_set:
                midi.addNote(track_idx, channel_cursor, play_note - 12, time_cursor + t_off, 0.8, vol + 20)
                cp_note = full_cp[i]
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + 1 + t_off, 0.7, vol - 15)
                midi.addNote(track_idx, channel_cursor, cp_note - 12, time_cursor + 2 + t_off, 0.7, vol - 15)
            
            elif inst_name == "Nylon Guitar" and inst_name not in melody_set:
                midi.addNote(track_idx, channel_cursor, play_note - 12, time_cursor + t_off, 0.8, vol - 10)
                cp_note = full_cp[i]
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + 1 + t_off, 0.8, vol - 20)
                midi.addNote(track_idx, channel_cursor, cp_note - 12, time_cursor + 2 + t_off, 0.8, vol - 20)

            else:
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + t_off, MEASURE_LEN * d_fac, vol)

            time_cursor += MEASURE_LEN 
            
        track_idx += 1
        channel_cursor += 1 

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    
    print(f"\n[+] DOSYA KAYDEDİLDİ: {filename}")

def generate_full_song_structure():
    song_structure = []
    verse_block = verse_theme_a + verse_theme_b
    chorus_block = chorus_high + chorus_low
    
    song_structure.append(intro_outro) 
    song_structure.append(verse_block)
    song_structure.append(verse_block)
    song_structure.append(pre_chorus)
    song_structure.append(chorus_block)
    song_structure.append(intro_outro)
    song_structure.append(verse_block)
    song_structure.append(pre_chorus)
    
    solo_section_content = solo_theme + solo_theme 
    song_structure.append(solo_section_content) 
    
    song_structure.append(chorus_block)
    song_structure.append(chorus_block)
    song_structure.append(intro_outro)
    song_structure.append([64, 64, 64, 64]) 

    full_cf = []
    full_cp = []
    solo_start_index = 0
    solo_end_index = 0
    current_note_count = 0
    
    print(f"\n[>] Hijo de la Luna (Split Choir Mix) Hazırlanıyor...")
    
    for section in song_structure:
        is_this_solo = (section == solo_section_content)
        if is_this_solo:
            solo_start_index = current_note_count
            solo_end_index = current_note_count + len(section)

        solver = UniversalBaroqueSolver(section, key_root_name='E', mode='minor')
        solver.target_solutions = 150 
        result = solver.solve()
        
        if is_this_solo:
            full_cf.extend(section)
            full_cp.extend(section) 
        elif result:
            full_cf.extend(section)
            full_cp.extend(result['melody'])
        else:
            full_cf.extend(section)
            full_cp.extend(section)
        current_note_count += len(section)

    return full_cf, full_cp, (solo_start_index, solo_end_index)

if __name__ == "__main__":
    cf, cp, solo_range = generate_full_song_structure()
    
    if cf:
        orchestra_config = {
            # Melodiye "Choir Soprano" ekledik (Violin ile beraber melodiyi söyler)
            "melody_instruments": ["Violin", "Flute", "Choir Soprano"], 
            
            # Basa "Choir Bass" ekledik (Piyano ile beraber altyapıyı söyler)
            "bass_instruments": [
                "Grand Piano",     
                "String Ensemble", 
                "Choir Bass",
                "Voice Oohs",      
                "Cello",           
                "Contrabass",      
                "Nylon Guitar"     
            ] 
        }
        
        output_file = "Hijo_SplitChoir_Auto.mid"
        
        # 1. MIDI'yi Kaydet
        save_orchestrated_waltz_midi(cf, cp, orchestra_config, output_file, solo_range)
        
        # 2. Grafik Çiz (PNG)
        analyze_composition(cf, cp, output_file)
        
        # 3. PDF Oluştur (MuseScore 4)
        convert_midi_to_pdf(output_file)