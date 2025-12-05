import random
import sys
from midiutil import MIDIFile

# --- MOTOR KONTROLÜ ---
try:
    from baroque_engine import UniversalBaroqueSolver 
except ImportError:
    print("\n[!] HATA: 'baroque_engine.py' dosyası bulunamadı.")
    sys.exit(1)

# --- MELODİK YAPI (THE GODFATHER - E Minor) ---
theme_a = [59, 64, 67, 63, 64, 71, 69, 67, 64, 60, 62]
theme_b = [59, 64, 67, 63, 64, 71, 69, 67, 64, 60, 59]
chorus_high = [69, 72, 69, 68, 69, 76, 74, 72, 71, 69, 68, 69]
chorus_low  = [69, 67, 66, 64, 63, 64]
intro_outro = [64, 60, 59, 60, 64] 
solo_theme  = [71, 76, 79, 75, 76, 83, 81, 79, 76, 72, 74]

# --- ENSTRÜMAN LİSTESİ ---
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

def get_human_touch(inst_name, measure_len, base_velocity):
    """ Robotikliği önleyen fonksiyon """
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
    """ MIDI Dosyasını Oluşturan Fonksiyon """
    num_tracks = len(arrangement["melody_instruments"]) + len(arrangement["bass_instruments"])
    midi = MIDIFile(num_tracks) 
    START_BPM = 105
    MEASURE_LEN = 3.0 
    track_idx = 0
    channel_cursor = 0 
    solo_start, solo_end = solo_range
    total_measures = len(full_cp)

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
            # --- RITARDANDO (Yavaşlama) ---
            if track_idx == 0:
                measures_left = total_measures - i
                if measures_left <= 5:
                    drop_amount = (6 - measures_left) * 10 
                    new_bpm = max(60, START_BPM - drop_amount)
                    midi.addTempo(track_idx, time_cursor, new_bpm)

            # --- SOLO KONTROLÜ ---
            is_solo_section = (solo_start <= i < solo_end)
            if inst_name in melody_set and is_solo_section and inst_name != "Flute":
                time_cursor += MEASURE_LEN
                continue 

            # --- NOTA HESAPLAMA ---
            play_note = note
            if inst_name == "Flute": play_note += 12
            if inst_name in ["Cello", "Contrabass", "Choir Bass"]: play_note -= 12 

            # Velocity (Ses Şiddeti)
            base_vol = 95
            if inst_name == "Flute": base_vol = 105 if is_solo_section else 90
            elif inst_name == "Grand Piano": base_vol = 100
            elif inst_name == "Choir Soprano": base_vol = 65
            elif inst_name == "Choir Bass": base_vol = 60
            
            t_off, d_fac, vol = get_human_touch(inst_name, MEASURE_LEN, base_vol)
            
            # --- ARPEJ MANTIĞI ---
            if inst_name == "Grand Piano" and inst_name not in melody_set:
                midi.addNote(track_idx, channel_cursor, play_note - 12, time_cursor + t_off, 0.8, vol + 20)
                
                current_melody_note = full_cp[i] if i < len(full_cp) else play_note
                arp_speed = 0.05 
                
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + 1 + t_off, 0.7, vol - 10)
                midi.addNote(track_idx, channel_cursor, current_melody_note - 12, time_cursor + 1 + t_off + arp_speed, 0.7, vol - 15)
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + 2 + t_off, 0.7, vol - 10)
                midi.addNote(track_idx, channel_cursor, current_melody_note - 12, time_cursor + 2 + t_off + arp_speed, 0.7, vol - 15)
            
            elif inst_name == "Nylon Guitar" and inst_name not in melody_set:
                midi.addNote(track_idx, channel_cursor, play_note - 12, time_cursor + t_off, 0.8, vol - 10)
                current_melody_note = full_cp[i] if i < len(full_cp) else play_note
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + 1 + t_off, 0.8, vol - 20)
                midi.addNote(track_idx, channel_cursor, current_melody_note - 12, time_cursor + 2 + t_off, 0.8, vol - 20)
            else:
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + t_off, MEASURE_LEN * d_fac, vol)

            time_cursor += MEASURE_LEN 
        track_idx += 1
        channel_cursor += 1 

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    print(f"\n[+] BAŞARILI: {filename} dosyası oluşturuldu.")

def solve_atomically(segment):
    """
    DONMAYI ÖNLEYEN FONKSİYON:
    Melodiyi 'chunk'lara bölmek yerine TEK TEK (Atomic) motora sorar.
    Backtracking derinliği oluşmadığı için asla donmaz.
    """
    final_cf = [] # Bas
    final_cp = [] # Melodi

    # Her bir notayı tek tek işliyoruz (Size = 1)
    for note in segment:
        chunk = [note]
        
        # Engine'i çağır ama sadece 1 nota için
        solver = UniversalBaroqueSolver(chunk, key_root_name='E', mode='minor')
        solver.target_solutions = 1
        
        try:
            result = solver.solve()
            if result:
                final_cf.extend(chunk)
                final_cp.extend(result['melody'])
            else:
                # Motor bulamazsa unison
                final_cf.extend(chunk)
                final_cp.extend(chunk)
        except Exception:
             final_cf.extend(chunk)
             final_cp.extend(chunk)
             
    return final_cf, final_cp

def generate_full_song_structure():
    song_structure = []
    
    # Godfather Yapısı
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
    
    print(f"\n[>] Godfather Waltz (Atomic Engine Mode) Hazırlanıyor...")
    
    for i, section in enumerate(song_structure):
        is_this_solo = (section == solo_section_content)
        if is_this_solo:
            solo_start_index = current_note_count
            solo_end_index = current_note_count + len(section)
            # Soloda motor kullanma, unison devam et
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
        save_orchestrated_midi(cf, cp, orchestra_config, "Godfather_baroque.mid", solo_range)