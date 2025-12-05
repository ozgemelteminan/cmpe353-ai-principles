import random

# --- KURALLAR ---
class CounterpointRules:
    def __init__(self):
        self.consonances = {0, 3, 4, 7, 8, 9}
        self.dissonances = {1, 2, 5, 6, 10, 11}
        self.forbidden_melodic_intervals = {6, 11, 13}

    def get_interval(self, n1, n2): return abs(n1 - n2)
    def get_interval_class(self, n1, n2): return abs(n1 - n2) % 12
    def get_direction(self, prev_n, curr_n):
        if curr_n > prev_n: return 1
        if curr_n < prev_n: return -1
        return 0
    def is_step(self, n1, n2): return abs(n1 - n2) in {1, 2}
    def is_skip(self, n1, n2): return abs(n1 - n2) >= 3
    def is_consonant(self, n1, n2): return (abs(n1 - n2) % 12) in self.consonances
    def is_perfect(self, n1, n2): return (abs(n1 - n2) % 12) in {0, 7}

    # Hard Constraints
    def hc_parallel_fifths_octaves(self, cf_prev, cf_curr, cp_prev, cp_curr):
        int_prev = self.get_interval_class(cf_prev, cp_prev)
        int_curr = self.get_interval_class(cf_curr, cp_curr)
        if int_curr in {0, 7} and int_prev == int_curr:
            if self.get_direction(cf_prev, cf_curr) == self.get_direction(cp_prev, cp_curr):
                return False
        return True

    def hc_consonant_interval(self, cf_curr, cp_curr, is_strong_beat):
        if is_strong_beat:
            interval = self.get_interval(cf_curr, cp_curr)
            if (interval % 12) in self.dissonances: return False
            if interval > 24: return False
        return True

    def hc_suspension_resolution(self, cf_prev, cp_prev, cf_curr, cp_curr):
        if not self.is_consonant(cf_prev, cp_prev):
            if self.get_direction(cp_prev, cp_curr) != -1: return False
            if not self.is_step(cp_prev, cp_curr): return False
            if not self.is_consonant(cf_curr, cp_curr): return False
        return True

    def hc_no_augmented_melodic(self, cp_prev, cp_curr):
        diff = abs(cp_curr - cp_prev)
        if diff in self.forbidden_melodic_intervals or diff > 12: return False
        return True

    # Soft Constraints
    def sc_accented_dissonance(self, cf_prev, cf_curr, cp_prev, cp_curr, cp_next, is_strong_beat):
        if is_strong_beat:
            if not self.is_consonant(cf_curr, cp_curr):
                if self.is_skip(cp_prev, cp_curr):
                    if cp_next is not None:
                        if self.is_step(cp_curr, cp_next) and self.get_direction(cp_curr, cp_next) == -1:
                            return 5
        return 0

    def sc_passing_tone(self, cf_curr, cp_prev, cp_curr, cp_next, is_strong_beat):
        if not is_strong_beat:
            if not self.is_consonant(cf_curr, cp_curr):
                if self.is_step(cp_prev, cp_curr):
                    if cp_next is not None:
                         if self.is_step(cp_curr, cp_next) and \
                            self.get_direction(cp_prev, cp_curr) == self.get_direction(cp_curr, cp_next):
                             return 2
        return 0

    def sc_contrary_motion(self, cf_prev, cf_curr, cp_prev, cp_curr):
        dir_cf = self.get_direction(cf_prev, cf_curr)
        dir_cp = self.get_direction(cp_prev, cp_curr)
        if dir_cf != 0 and dir_cp != 0 and dir_cf != dir_cp: return 2
        return 0

    def sc_hidden_parallels(self, cf_prev, cf_curr, cp_prev, cp_curr):
        int_curr = self.get_interval_class(cf_curr, cp_curr)
        if int_curr in {0, 7}:
            if self.get_direction(cf_prev, cf_curr) == self.get_direction(cp_prev, cp_curr):
                if self.is_skip(cp_prev, cp_curr): return -5
        return 0

    def sc_close_position(self, cf_curr, cp_curr):
        if self.get_interval(cf_curr, cp_curr) < 16: return 1
        return 0

# --- KONTROL FONKSIYONLARI ---
def check_hard_constraints_verbose(rules, cf_notes, cp_notes, current_idx, indent=""):
    if current_idx == 0: return True
    cf_prev, cf_curr = cf_notes[current_idx-1], cf_notes[current_idx]
    cp_prev, cp_curr = cp_notes[current_idx-1], cp_notes[current_idx]
    is_strong = (current_idx % 2 == 0)

    # Ozel Kural: Bitis (Tonik/Oktav)
    if current_idx == len(cf_notes) - 1:
        if (abs(cf_curr - cp_curr) % 12) != 0: return False

    if not rules.hc_parallel_fifths_octaves(cf_prev, cf_curr, cp_prev, cp_curr): return False
    if not rules.hc_consonant_interval(cf_curr, cp_curr, is_strong): return False 
    if not rules.hc_suspension_resolution(cf_prev, cp_prev, cf_curr, cp_curr): return False
    if not rules.hc_no_augmented_melodic(cp_prev, cp_curr): return False
    return True

def calculate_total_score_verbose(rules, cf_notes, cp_notes):
    score = 0
    for i in range(1, len(cp_notes)):
        cf_prev, cf_curr = cf_notes[i-1], cf_notes[i]
        cp_prev, cp_curr = cp_notes[i-1], cp_notes[i]
        cp_next = cp_notes[i+1] if i+1 < len(cp_notes) else None
        is_strong = (i % 2 == 0)
        
        score += rules.sc_accented_dissonance(cf_prev, cf_curr, cp_prev, cp_curr, cp_next, is_strong)
        score += rules.sc_passing_tone(cf_curr, cp_prev, cp_curr, cp_next, is_strong)
        score += rules.sc_contrary_motion(cf_prev, cf_curr, cp_prev, cp_curr)
        score += rules.sc_hidden_parallels(cf_prev, cf_curr, cp_prev, cp_curr)
        score += rules.sc_close_position(cf_curr, cp_curr)
    return score

# --- EVRENSEL SOLVER  ---

class UniversalBaroqueSolver:
    def __init__(self, cantus_firmus, key_root_name='C', mode='major'):
        self.cf = cantus_firmus
        self.rules = CounterpointRules()
        self.solutions = []
        self.min_interval = 0  
        self.max_interval = 16
        self.target_solutions = 1000 
        
        # --- TON AYARLAMA MOTORU ---
        self.key_root_name = key_root_name
        self.mode = mode
        self.allowed_pitch_classes = self._generate_scale_filter()
        print(f"[i] Ton Ayarlandi: {key_root_name} {mode.capitalize()}")
        print(f"[i] Izin Verilen Nota Siniflari: {self.allowed_pitch_classes}")

    def _generate_scale_filter(self):
        """
        Verilen kok ses ve moda gore izin verilen MIDI modlarini hesaplar.
        Ornek: Eb Major -> {3, 5, 7, 8, 10, 0, 2}
        """
        # Nota Ismi -> MIDI Numarasi (0-11)
        note_map = {
            'C':0, 'C#':1, 'DB':1, 'D':2, 'D#':3, 'EB':3, 
            'E':4, 'F':5, 'F#':6, 'GB':6, 'G':7, 'G#':8, 
            'AB':8, 'A':9, 'A#':10, 'BB':10, 'B':11
        }
        
        root = note_map[self.key_root_name.upper()]
        
        # Skala Formulleri (Semiton farklari)
        if self.mode.lower() == 'major':
            intervals = [0, 2, 4, 5, 7, 9, 11] # Major Skala
        else:
            # Harmonik Minor (Barok icin daha uygun - 7. derece artirilmis)
            intervals = [0, 2, 3, 5, 7, 8, 11] 
            
        # Kok sese gore kaydirma (Transpoze)
        allowed = set()
        for interval in intervals:
            allowed.add((root + interval) % 12)
            
        return allowed

    def get_valid_candidates(self, idx, current_melody, indent):
        cf_note = self.cf[idx]
        candidates = []
        
        possible_notes = list(range(self.min_interval, self.max_interval + 1))
        
        # --- HEURISTIC SIRALAMA ---
        def heuristic_score(interval):
            candidate_note = cf_note + interval
            score = 0
            
            # 1. Ton Filtresi (Burada eksi puan veriyoruz ki sirada en sona gitsin)
            if (candidate_note % 12) not in self.allowed_pitch_classes:
                return -1000 
            
            if idx > 0:
                prev_cp = current_melody[-1]
                prev_cf = self.cf[idx-1]
                
                # Zit Yon (+3)
                dir_cf = 1 if cf_note > prev_cf else (-1 if cf_note < prev_cf else 0)
                dir_cp = 1 if candidate_note > prev_cp else (-1 if candidate_note < prev_cp else 0)
                if dir_cf != 0 and dir_cp != 0 and dir_cf != dir_cp:
                    score += 3
                
                # Adim Hareketi (+2)
                step_size = abs(candidate_note - prev_cp)
                if step_size <= 2: score += 2
                elif step_size > 4: score -= 2

            # Kusurlu Konsonans (+1)
            if (interval % 12) in {3, 4, 8, 9}: score += 1
            
            return score

        possible_notes.sort(key=heuristic_score, reverse=True)

        for interval in possible_notes:
            candidate_note = cf_note + interval
            
            # KESIN FILTRE: Ton disi notalari hic deneme
            if (candidate_note % 12) not in self.allowed_pitch_classes:
                continue

            temp_cp = current_melody + [candidate_note]

            if check_hard_constraints_verbose(self.rules, self.cf, temp_cp, idx, indent):
                candidates.append(candidate_note)
            
        return candidates

    def backtrack(self, current_melody, depth=0):
        indent = "  " * depth 
        idx = len(current_melody)
        
        if len(self.solutions) >= self.target_solutions: return

        if idx == len(self.cf):
            score = calculate_total_score_verbose(self.rules, self.cf, current_melody)
            self.solutions.append({'melody': list(current_melody), 'score': score})
            return 

        candidates = self.get_valid_candidates(idx, current_melody, indent)
        if not candidates: return 

        for note in candidates:
            current_melody.append(note)
            self.backtrack(current_melody, depth + 1)
            if len(self.solutions) >= self.target_solutions: return
            current_melody.pop() 

    def solve(self):
        print(f"[>] Barok Kontrpuan Arayisi Basliyor ({self.key_root_name} {self.mode})...")
        self.backtrack([])
        
        if not self.solutions:
            print("[!] Hicbir gecerli cozum bulunamadi.")
            return None
            
        self.solutions.sort(key=lambda x: x['score'], reverse=True)
        best = self.solutions[0]
        print(f"\n[OK] Arama Tamamlandi. ({len(self.solutions)} aday)")
        print(f"[*] EN IYI SONUC (Puan: {best['score']})")
        return best

# --- TEST ---
if __name__ == "__main__":
    # ORNEK: Mecano - Hijo de la Luna
    # Orijinal Ton: Mi Minor (E Minor) - Armaturde 1 Diyez (F#)
    
    # Melodinin Ana Temasi (Verse Kismi - Sadelesmis)
    # Notalar: B4, C5, B4, A4, G4, F#4, E4, F#4, A4, G4, F#4, E4
    cf_luna = [71, 72, 71, 69, 67, 66, 64, 66, 69, 67, 66, 64]
    
    print("\n Parça: Hijo de la Luna (Barok Stil Uyarlamasi)")
    
    # Solver'i 'E' (Mi) ve 'Minor' olarak baslatiyoruz
    solver = UniversalBaroqueSolver(cf_luna, key_root_name='E', mode='minor')
    result = solver.solve()
    
    if result:
        # Nota isimlerine cevirme fonksiyonu (E Minor'e uygun diyezli gosterim)
        def midi_to_note_name(midi_num):
            # Diyezli notalar tercih edilir (E Minor oldugu icin)
            note_names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
            note = note_names[midi_num % 12]
            octave = (midi_num // 12) - 1
            return f"{note}{octave}"

        readable_cf = [midi_to_note_name(n) for n in cf_luna]
        readable_cp = [midi_to_note_name(n) for n in result['melody']]
        
        print("\n--- SONUCLAR ---")
        print("Cantus Firmus (MIDI):", cf_luna)
        print("Cantus Firmus (Nota):", readable_cf)
        print("Kontrpuan (MIDI)    :", result['melody'])
        print("Kontrpuan (Nota)    :", readable_cp)



