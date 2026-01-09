import random
import os
import time
import sys

# ===== TABLES =====
TRACK_TYPES = [
    "One-Shot Drums", "Drum Loop", "Percussion", "Bass", "Lead", "Chord", "Pad",
    "Piano/Keys", "Sample", "FX or Texture", "Arp/Sequence", "Vocal/Voice",
    "Acoustic Instrument", "Electric Instrument", "Player's Choice"
]

MUTATIONS = {1: "Sum the Track to mono.", 3: "Track must be monophonic.", 5: "Limited to one octave or four slices.",
             7: "Notes/slices must be fixed velocity.", 9: "Track must loop one bar over and over.",
             11: "May only play on beats 1 and 3.", 13: "May only play on beats 2 and 4.",
             15: "Must be played or sequenced in triplets.", 17: "May not be quantized; must be performed live.",
             19: "Must be quantized to 1/16 steps.", 21: "Must be programmed in a step sequencer.",
             23: "Notes/slices can't be edited after they've been performed/programmed.",
             25: "Cannot be re-sequenced after the Room resolves. Can only delete notes/slices.",
             27: "Must be altered and resampled before composing.", 29: "Shorten envelope to be percussive.",
             31: "Must use one sound or note only.", 33: "Cannot use the same note or slice twice.",
             35: "Notes must be played in strict order (low->high / first->last).",
             37: "Every note must repeat once before another may be played.",
             39: "There can be no silence in the Track.", 41: "Must pass through reverb before composing.",
             43: "Must pass through delay before composing.", 45: "May not use effects.",
             47: "May use only one effect.", 49: "Must be side-chained to the previous Track.",
             51: "Must be noise-gated.", 53: "Must pass through a low-pass filter (1 kHz).",
             55: "Must be detuned slightly +/-10 cents.", 57: "You can't audition sounds. Pick blind before composing.",
             59: "All effects must be added and tuned before you choose a sound.",
             61: "Mute all rhythms and the metronome for the duration of the Room.",
             63: "Roll twice. Apply both Mutations.", 65: "Only apply effects that have already been used.",
             67: "Must include one deliberate wrong note.", 69: "No Mutation.",
             71: "Track must abandon its intended Track Type.",
             73: "Solo this Track for the duration of the Room. Metronome allowed.",
             75: "Only use effects that haven't been used.", 77: "Once Room is Finalized, volume is locked.",
             79: "No Mutation.", 81: "No Mutation.", 83: "Purpose of Track changes to match previous Room.",
             85: "Repeat the last Room's Mutation.",
             87: "Once you begin composing, The Room finalizes in three minutes.",
             89: "Must contain the same amount of notes as Target Track.",
             91: "Compose Track while it's muted. No unmute until Room is Finalized.",
             93: "Each note on this track requires deleting one note from another Track.",
             95: "Take a Target Curse instead.", 97: "Once a note or slice is placed, it can't be moved, only deleted.",
             99: "Roll afterward. 80 or higher = delete Track."}
TARGET_CURSES = {1: "Mute until end of run.", 5: "Collapse to mono.", 9: "1/32 quantize.",
                 13: "Pan hard left or right.", 17: "Track must remain constant in the final arrangement.",
                 21: "Resample, Chop, Reverse, Re-sequence.", 25: "Pitch shift one octave.",
                 29: "Apply Flanger or Chorus.", 33: "Force a Room. The next Room will have two Mutations.",
                 37: "Turn Track down -6 db.", 41: "Strip all effects.",
                 45: "This Track is now the target of all future Curses until end of Run.", 49: "Over-compress.",
                 53: "Roll d100 on end. 51+ forces another Room.", 57: "Delete Track.",
                 61: "No Re-sequencing or Volume change.", 65: "Remove half the notes/chops.",
                 69: "Loop a short segment.", 73: "Erase all notes/slices except first and last.",
                 77: "This Track can't loop back to back.", 81: "Delete the first bar.", 85: "Delete the last bar.",
                 89: "Cannot edit Track rest of Run.", 93: "Apply last Curse to another track.", 97: "Re-roll Twice."}


# ===== CORE ENGINE =====
class GameState:
    def __init__(self, seed):
        self.seed = seed
        random.seed(seed)
        self.current_room = 1
        self.power_ups = 0
        self.active_curses = []
        self.rooms_history = []


def clear_screen():
    """Clears the terminal without creating 'empty space' errors."""
    if os.name == 'nt':
        os.system('cls')
    elif os.environ.get('TERM') and sys.stdout.isatty():
        os.system('clear')
    else:
        # If no real terminal is detected, just print a divider to avoid blank space
        print("\n" + "-" * 30 + " REFRESH " + "-" * 30 + "\n")


def header(state):
    print("=" * 65)
    print(f"⚔️  SUPER BEATMAKER by Jon Makes Beats | Seed: {state.seed}")
    print(f"Room: {state.current_room} | ⚡ Power-ups: {state.power_ups} | 🔴 Curses: {len(state.active_curses)}")
    print("=" * 65)


def play_room(state, mode="manual"):
    room_data = {"number": state.current_room, "name": "Untitled", "track_type": "", "mutation": "", "curse": "",
                 "notes": ""}

    clear_screen()
    header(state)

    # 1. Track Name (Skipped in Autoplay)
    if mode == "manual":
        name_input = input("\n[Step 1] Room/Track Name (Optional): ").strip()
        if name_input: room_data["name"] = name_input

    # 2. Track Type
    if mode == "manual":
        print("\n[Step 2] Select Track Type")
        for i, t in enumerate(TRACK_TYPES, 1): print(f"{i}. {t}")
        try:
            choice = int(input("\nSelect (1-15): "))
            room_data["track_type"] = TRACK_TYPES[choice - 1]
        except:
            room_data["track_type"] = "Player's Choice"
    else:
        roll = random.randint(1, 100)
        idx = min((roll - 1) // 7, len(TRACK_TYPES) - 1)
        room_data["track_type"] = TRACK_TYPES[idx]
        print(f"\n[Step 2] Track Type (Random): {room_data['track_type']}")

    # 3. Mutation
    if mode != "autoplay": input("\n[Step 3] Press Enter to roll Mutation...")
    m_roll = random.randint(1, 100)
    key = ((m_roll - 1) // 2) * 2 + 1
    room_data["mutation"] = MUTATIONS.get(key, "No Mutation.")
    print(f"MUTATION: {room_data['mutation']}")

    # 4. Curse
    if state.current_room > 1:
        if mode != "autoplay": input("\n[Step 4] Press Enter for Curse Check...")
        if random.randint(1, 100) > 70:
            t_roll = random.randint(1, 100)
            key_c = ((t_roll - 1) // 4) * 4 + 1
            curse = TARGET_CURSES.get(key_c, "Unknown Curse")
            room_data["curse"] = curse
            state.active_curses.append(f"Room {state.current_room}: {curse}")
            print(f"⚠️ CURSED: {curse}")
        else:
            print("✓ Safe (No Curse)")

    # 5. Power-up
    if random.randint(1, 100) >= 76:
        state.power_ups += 1
        print("\n✨ You gained a Power-Up!")

    # 6. Notes
    room_data["notes"] = input("\n[Step 5] Enter Notes: ")

    state.rooms_history.append(room_data)
    state.current_room += 1


def show_history(state):
    clear_screen()
    print("📜 RUN HISTORY")
    print("-" * 30)
    if not state.rooms_history:
        print("No rooms completed yet.")
    for r in state.rooms_history:
        print(f"Room {r['number']} [{r['name']}]: {r['track_type']}")
        print(f"  - Mutation: {r['mutation']}")
        if r['curse']: print(f"  - Curse: {r['curse']}")
        if r['notes']: print(f"  - Notes: {r['notes']}")
        print("-" * 20)
    input("\nPress Enter to return to menu...")


def main_game_loop():
    clear_screen()
    print("Welcome to Super Beatmaker by Jon Makes Beats")
    print("Please support the creator: https://www.patreon.com/c/jonmakesbeats/posts")
    print("-" * 60)

    random_seed = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
    print(f"Generated Seed: {random_seed}")
    time.sleep(1)

    state = GameState(random_seed)

    while True:
        clear_screen()
        header(state)
        print("\n1. Next Room (Manual Track Type)")
        print("2. Next Room (Random Track Type)")
        print("3. Autoplay Room (Random Track and Instant Mutations/Curses)")
        print("4. View History/Notes")
        print("5. End Run and Save")

        choice = input("\nChoice: ")

        if choice == "1":
            play_room(state, "manual")
        elif choice == "2":
            play_room(state, "random")
        elif choice == "3":
            play_room(state, "autoplay")
        elif choice == "4":
            show_history(state)
        elif choice == "5":
            break

    # Final Save
    clear_screen()
    print("🏁 RUN COMPLETE")
    print("The goal of this game is to make music while experiencing the constraints and curveballs of external sources. \nIf this system made you think about making music in new ways, you won!")
    print("Please support the creator: https://www.patreon.com/jonmakesbeats/posts")
    save_path = input("\nWhere would you like to save run.txt? (Press Enter for default): ").strip()
    if not save_path: save_path = "run.txt"

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(f"SUPER BEATMAKER LOG - Seed: {state.seed}\n" + "=" * 40 + "\n")
            for r in state.rooms_history:
                f.write(f"ROOM {r['number']} ({r['name']})\nType: {r['track_type']}\nMutation: {r['mutation']}\n")
                if r['curse']: f.write(f"Curse: {r['curse']}\n")
                f.write(f"Notes: {r['notes']}\n" + "-" * 20 + "\n")
        print(f"\nSaved to: {os.path.abspath(save_path)}")
    except Exception as e:
        print(f"Save error: {e}")


def run_app():
    while True:
        main_game_loop()
        print("\n" + "=" * 30)
        again = input("Would you like to start a NEW run? (y/n): ").lower()
        if again != 'y':
            print("Thanks for playing!")
            time.sleep(1)
            break


if __name__ == "__main__":
    run_app()
