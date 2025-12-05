import random
from midiutil import MIDIFile
from baroque_engine import UniversalBaroqueSolver 

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
    "Choir Soprano":     {"pan": 40,  "reverb": 100}, 
    "Choir Bass":        {"pan": 90,  "reverb": 100}  
}

def get_human_touch(inst_name, measure_len, base_velocity):
    timing_offset = random.uniform(-0.01, 0.01) 
    duration_factor = 0.95 
    velocity = base_velocity + random.randint(-5, 5)

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
    
    # Başlangıç Temposu
    START_BPM = 148
    MEASURE_LEN = 3.0 
    
    track_idx = 0
    channel_cursor = 0 
    solo_start, solo_end = solo_range

    all_instruments = arrangement["melody_instruments"] + arrangement["bass_instruments"]
    melody_set = set(arrangement["melody_instruments"])

    # Şarkının toplam uzunluğunu bul (Ritardando hesaplamak için)
    total_measures = len(full_cp)

    for inst_name in all_instruments:
        if channel_cursor == 9: channel_cursor += 1
            
        program_num = INSTRUMENTS.get(inst_name, 0)
        midi.addTrackName(track_idx, 0, inst_name)
        midi.addProgramChange(track_idx, channel_cursor, 0, program_num)
        
        # İlk başta tempoyu ayarla
        midi.addTempo(track_idx, 0, START_BPM)
        
        settings = MIXER_SETTINGS.get(inst_name, {"pan": 64, "reverb": 40})
        midi.addControllerEvent(track_idx, channel_cursor, 0, 10, settings["pan"])
        midi.addControllerEvent(track_idx, channel_cursor, 0, 91, settings["reverb"])

        time_cursor = 0
        note_list = full_cp if inst_name in melody_set else full_cf
        
        for i, note in enumerate(note_list):
            
            # --- RITARDANDO (YAVAŞLAMA) MANTIĞI ---
            # Sadece 1. kanalda tempo kontrolü yapalım ki çakışma olmasın
            if track_idx == 0:
                measures_left = total_measures - i
                # Son 4 ölçüde yavaşlamaya başla
                if measures_left <= 4:
                    # Formül: Her ölçüde tempoyu biraz daha düşür
                    # 148 -> 130 -> 110 -> 90 -> 80 gibi
                    drop_amount = (5 - measures_left) * 15 
                    new_bpm = max(80, START_BPM - drop_amount)
                    midi.addTempo(track_idx, time_cursor, new_bpm)

            # Solo Kontrolü
            is_solo_section = (solo_start <= i < solo_end)
            if inst_name in melody_set and is_solo_section and inst_name != "Flute":
                time_cursor += MEASURE_LEN
                continue 

            play_note = note
            if inst_name == "Flute": play_note += 12
            if inst_name in ["Cello", "Contrabass", "Choir Bass"]: play_note -= 12 

            base_vol = 95
            if inst_name == "Flute": base_vol = 100 if is_solo_section else 90
            elif inst_name == "Grand Piano": base_vol = 100
            elif inst_name == "Choir Soprano": base_vol = 65
            elif inst_name == "Choir Bass": base_vol = 60
            
            t_off, d_fac, vol = get_human_touch(inst_name, MEASURE_LEN, base_vol)
            
            # --- ARPEJ VE NOTA YAZMA ---
            
            if inst_name == "Grand Piano" and inst_name not in melody_set:
                # Piyano Ritim: PUM - Tı-rın - Tı-rın (Arpejli)
                
                # 1. Vuruş (Bas) - Güçlü
                midi.addNote(track_idx, channel_cursor, play_note - 12, time_cursor + t_off, 0.8, vol + 20)
                
                cp_note = full_cp[i]
                
                # ARPEJ HIZI (Notalar arasındaki milisaniyelik fark)
                arp_speed = 0.04 

                # 2. Vuruş (Arpejli Akor)
                # İlk nota
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + 1 + t_off, 0.7, vol - 10)
                # İkinci nota biraz gecikmeli gelir (Arpej etkisi)
                midi.addNote(track_idx, channel_cursor, cp_note - 12, time_cursor + 1 + t_off + arp_speed, 0.7, vol - 15)

                # 3. Vuruş (Arpejli Akor)
                midi.addNote(track_idx, channel_cursor, play_note, time_cursor + 2 + t_off, 0.7, vol - 10)
                midi.addNote(track_idx, channel_cursor, cp_note - 12, time_cursor + 2 + t_off + arp_speed, 0.7, vol - 15)
            
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
    print("[i] Özellikler: Split Choir + Piano Arpeggios + Final Ritardando.")

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
    
    print(f"\n[>] Hijo de la Luna (Final Masterpiece) Hazırlanıyor...")
    
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
            "melody_instruments": ["Violin", "Flute", "Choir Soprano"], 
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
        save_orchestrated_waltz_midi(cf, cp, orchestra_config, "Hijo_Masterpiece_baroque.mid", solo_range)
        