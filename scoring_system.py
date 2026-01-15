import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog # Import filedialog for saving files
import json
import os
from ctypes import windll
import csv # Import csv module for CSV operations

# Ensure proper scaling on high-DPI displays
windll.shcore.SetProcessDpiAwareness(1)

# --- Configuration Constants ---
DATA_FILE = "tournament_data.json"
NUM_TEAMS = 5
MEMBERS_PER_TEAM = 4


# Global data structures
teams_data = {}
selected_event_for_tournament = None


# Define events with their type and description
event_details = {
    "Ping Pong Tournament": {
        "type": "Tournament",
        "description": "Teams compete in a series of ping pong matches. Points: 3 per match won, 1 per match lost.",
    },
    "Video Game Tournament": {
        "type": "Tournament",
        "description": "Teams battle it out in a selected video game. Points: 3 per match won, 1 per match lost.",
    },
    "College Quiz": {
        "type": "Elimination",
        "description": "Teams answer a series of general knowledge questions; incorrect answers lead to elimination. Enter the final points awarded based on standing.",
    },
    "Spelling Bee": {
        "type": "Elimination",
        "description": "Teams participate in a spelling challenge. Teams are eliminated for incorrect spellings. Enter the final points awarded based on standing.",
    },
    "Scavenger Hunt": {
        "type": "Elimination",
        "description": "Teams follow clues to find hidden items around campus. Enter the final points awarded based on completion/items found.",
    }
}


# --- Utility Functions ---
def center_window(window, width=600, height=None): # Modified: height is now optional
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Temporarily set window to be visible but small to get correct dimensions
    window.update_idletasks() 

    # Calculate actual width/height if not provided, or use provided values
    if width is None:
        actual_width = window.winfo_reqwidth()
    else:
        actual_width = width
    
    if height is None:
        actual_height = window.winfo_reqheight()
    else:
        actual_height = height

    x = (screen_width // 2) - (actual_width // 2)
    y = (screen_height // 2) - (actual_height // 2)
    
    window.geometry(f"{actual_width}x{actual_height}+{x}+{y}")


# --- Data Persistence Functions ---
def save_data():
    """Saves the current teams_data, event_details, and selected_event to a JSON file."""
    data_to_save = {
        "teams": teams_data,
        "event_details": event_details,
        "selected_event": selected_event_for_tournament
    }
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        # Use global status_label (defined in main app setup)
        status_label.config(text=f"Data saved to {DATA_FILE}", fg="green")
    except Exception as e:
        status_label.config(text=f"Error saving data: {e}", fg="red")
        messagebox.showerror("Save Error", f"Failed to save data:\n{e}")

def load_data():
    """Loads teams_data, event_details, and selected_event from a JSON file."""
    global teams_data, event_details, selected_event_for_tournament
    if not os.path.exists(DATA_FILE):
        status_label.config(text=f"No existing data file '{DATA_FILE}' found. Starting fresh.", fg="orange")
        return False

    try:
        with open(DATA_FILE, 'r') as f:
            loaded_data = json.load(f)
        teams_data = loaded_data.get("teams", {})
        # Ensure event_details is updated without overwriting new default events
        for event_name, details in loaded_data.get("event_details", {}).items():
            event_details[event_name] = details
        selected_event_for_tournament = loaded_data.get("selected_event", None)
        status_label.config(text=f"Data loaded from {DATA_FILE}", fg="green")
        if selected_event_for_tournament:
            current_event_label.config(text=f"Current Event: {selected_event_for_tournament}")
        return True
    except json.JSONDecodeError as e:
        status_label.config(text=f"Error loading data: Invalid JSON format: {e}", fg="red")
        messagebox.showerror("Load Error", f"Corrupted data file. Failed to load:\n{e}")
        return False
    except Exception as e:
        status_label.config(text=f"Error loading data: {e}", fg="red")
        messagebox.showerror("Load Error", f"Failed to load data:\n{e}")
        return False

# --- Core Tournament Management Functions ---

def initialise_teams():
    if messagebox.askyesno("Confirm Initialisation",
                            f"This will reset all existing team data and member data. Do you want to initialise {NUM_TEAMS} empty teams?"):
        global teams_data
        teams_data = {}
        for i in range(1, NUM_TEAMS + 1):
            team_name = f"Team {i}"
            teams_data[team_name] = {
                "members": [],
                "event_scores": {},
                "total_score": 0
            }
        status_label.config(text=f"{NUM_TEAMS} default teams initialised.", fg="blue")
        save_data()

def manage_teams_popup():
    popup = tk.Toplevel(root)
    popup.title("Manage Teams and Members")
    center_window(popup, 700, 500) # Keep fixed size for team management

    tk.Label(popup, text="Select a Team to Manage:").pack(pady=5)

    team_names = list(teams_data.keys())
    if not team_names:
        tk.Label(popup, text="No teams initialised yet. Please initialise teams first.").pack()
        return

    selected_team_var = tk.StringVar(popup)
    selected_team_var.set(team_names[0])
    team_dropdown = tk.OptionMenu(popup, selected_team_var, *team_names)
    team_dropdown.pack(pady=5)

    current_members_label = tk.Label(popup, text="Current Members: None")
    current_members_label.pack(pady=5)

    def update_members_display(*args):
        team = selected_team_var.get()
        members = teams_data[team]["members"]
        current_members_label.config(text=f"Current Members ({len(members)}/{MEMBERS_PER_TEAM}): {', '.join(members) if members else 'None'}")

    selected_team_var.trace_add("write", update_members_display)
    update_members_display()

    tk.Label(popup, text="Add New Member Name:").pack(pady=5)
    new_member_entry = tk.Entry(popup)
    new_member_entry.pack(pady=2)

    member_msg_label = tk.Label(popup, text="", fg="red")
    member_msg_label.pack(pady=5)

    def add_member_to_team():
        team = selected_team_var.get()
        member_name = new_member_entry.get().strip()

        if not member_name:
            member_msg_label.config(text="Member name cannot be empty.", fg="red")
            return
        if member_name.isdigit():
            member_msg_label.config(text="Member name cannot be a number.", fg="red")
            return

        if member_name in teams_data[team]["members"]:
            member_msg_label.config(text=f"'{member_name}' is already in {team}.", fg="red")
            return

        if len(teams_data[team]["members"]) >= MEMBERS_PER_TEAM:
            member_msg_label.config(text=f"{team} already has {MEMBERS_PER_TEAM} members.", fg="red")
            return

        teams_data[team]["members"].append(member_name)
        new_member_entry.delete(0, tk.END)
        update_members_display()
        member_msg_label.config(text=f"'{member_name}' added to {team}.", fg="green")
        save_data()

    tk.Button(popup, text="Add Member", command=add_member_to_team).pack(pady=5)

    tk.Label(popup, text="Remove Member Name:").pack(pady=5)
    remove_member_entry = tk.Entry(popup)
    remove_member_entry.pack(pady=2)

    def remove_member_from_team():
        team = selected_team_var.get()
        member_name = remove_member_entry.get().strip()

        if not member_name:
            member_msg_label.config(text="Member name cannot be empty.", fg="red")
            return

        if member_name not in teams_data[team]["members"]:
            member_msg_label.config(text=f"'{member_name}' not found in {team}.", fg="red")
            return

        teams_data[team]["members"].remove(member_name)
        remove_member_entry.delete(0, tk.END)
        update_members_display()
        member_msg_label.config(text=f"'{member_name}' removed from {team}.", fg="green")
        save_data()

    tk.Button(popup, text="Remove Member", command=remove_member_from_team).pack(pady=5)


def select_event_popup():
    """Shows a popup to view all events and their descriptions, and allows selecting one."""
    global selected_event_for_tournament
    popup = tk.Toplevel(root)
    popup.title("View & Select Tournament Event")
    
    # Set the popup to fullscreen
    popup.attributes('-fullscreen', True)
    # Allow escaping fullscreen for the popup
    popup.bind("<Escape>", lambda e: popup.attributes('-fullscreen', False))

    tk.Label(popup, text="Available Events:", font=("Arial", 12, "bold")).pack(pady=10)

    event_options_frame = tk.Frame(popup)
    event_options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    selected_event_name_var = tk.StringVar(popup)
    if selected_event_for_tournament:
        selected_event_name_var.set(selected_event_for_tournament)

    canvas = tk.Canvas(event_options_frame)
    scrollbar = tk.Scrollbar(event_options_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


    for event_name, details in event_details.items():
        rb = tk.Radiobutton(scrollable_frame, text=event_name, variable=selected_event_name_var, value=event_name,
                            font=("Arial", 10, "bold"), anchor="w", justify=tk.LEFT)
        rb.pack(fill=tk.X, pady=2, padx=5)

        desc_label = tk.Label(scrollable_frame, text=f"Type: {details['type']}\n{details['description']}",
                              justify=tk.LEFT, wraplength=450, fg="gray")
        desc_label.pack(fill=tk.X, padx=15, pady=0)
        tk.Frame(scrollable_frame, height=1, bg="lightgray").pack(fill=tk.X, padx=5, pady=5)

    selection_msg_label = tk.Label(popup, text="", fg="red")
    selection_msg_label.pack(pady=5)

    button_frame = tk.Frame(popup)
    button_frame.pack(pady=10)

    def confirm_event_selection():
        global selected_event_for_tournament
        chosen_event = selected_event_name_var.get()
        if chosen_event:
            confirm = messagebox.askyesno("Confirm Event",
                                          f"Are you sure you want to select '{chosen_event}' as the primary event for this tournament? This will clear all existing event scores if you previously scored for other events.")
            if confirm:
                selected_event_for_tournament = chosen_event
                current_event_label.config(text=f"Current Event: {selected_event_for_tournament}")
                status_label.config(text=f"'{chosen_event}' selected as current event.", fg="blue")

                for team_name in teams_data:
                    teams_data[team_name]["event_scores"] = {} # Clear event_scores
                    teams_data[team_name]["total_score"] = 0   # Reset total_score
                save_data()
                popup.destroy()
            else:
                selection_msg_label.config(text="Event selection cancelled.")
        else:
            selection_msg_label.config(text="Please select an event.", fg="red")

    tk.Button(button_frame, text="Confirm Selection", command=confirm_event_selection).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Exit", command=popup.destroy).pack(side=tk.LEFT, padx=5)


def record_team_score_popup():
    popup = tk.Toplevel(root)
    popup.title("Record Team Scores")
    
    # Set the popup to fullscreen
    popup.attributes('-fullscreen', True)
    # Allow escaping fullscreen for the popup
    popup.bind("<Escape>", lambda e: popup.attributes('-fullscreen', False))

    global selected_event_for_tournament

    if not selected_event_for_tournament:
        tk.Label(popup, text="No event selected for the tournament. Please select an event first.").pack(pady=20)
        return
    if not teams_data:
        tk.Label(popup, text="No teams initialised. Please initialise teams first.").pack(pady=20)
        return

    tk.Label(popup, text=f"Recording scores for: {selected_event_for_tournament}",
             font=("Arial", 12, "bold"), fg="purple").pack(pady=5)

    tk.Label(popup, text="Select Team:").pack(pady=5)
    team_names = list(teams_data.keys())
    selected_team_var = tk.StringVar(popup)
    selected_team_var.set(team_names[0])
    team_dropdown = tk.OptionMenu(popup, selected_team_var, *team_names)
    team_dropdown.pack(pady=5)

    # Frame to hold dynamic input fields (wins/losses or direct points)
    dynamic_input_frame = tk.Frame(popup)
    dynamic_input_frame.pack(pady=10)

    score_msg_label = tk.Label(popup, text="", fg="red")
    score_msg_label.pack(pady=5)

    # These variables will hold the Entry widgets created dynamically
    wins_entry = None
    losses_entry = None
    points_entry = None

    def update_input_fields(*args):
        nonlocal wins_entry, losses_entry, points_entry # Declare non-local to modify the variables in the outer scope

        # Clear previous widgets from the dynamic frame
        for widget in dynamic_input_frame.winfo_children():
            widget.destroy()

        event_type = event_details[selected_event_for_tournament]["type"]
        team_name = selected_team_var.get() # Get selected team to pre-fill data

        if event_type == "Tournament":
            tk.Label(dynamic_input_frame, text="Matches Won:").pack(pady=2)
            wins_entry = tk.Entry(dynamic_input_frame)
            wins_entry.pack(pady=2)
            tk.Label(dynamic_input_frame, text="Matches Lost:").pack(pady=2)
            losses_entry = tk.Entry(dynamic_input_frame)
            losses_entry.pack(pady=2)
            
            # Pre-fill with existing scores if available for this team and event
            if selected_event_for_tournament in teams_data[team_name]["event_scores"]:
                event_score_data = teams_data[team_name]["event_scores"][selected_event_for_tournament]
                wins_entry.insert(0, str(event_score_data.get("wins", "")))
                losses_entry.insert(0, str(event_score_data.get("losses", "")))

        elif event_type == "Elimination":
            tk.Label(dynamic_input_frame, text="Final Points Awarded:").pack(pady=2)
            points_entry = tk.Entry(dynamic_input_frame)
            points_entry.pack(pady=2)
            
            # Pre-fill with existing scores if available
            if selected_event_for_tournament in teams_data[team_name]["event_scores"]:
                event_score_data = teams_data[team_name]["event_scores"][selected_event_for_tournament]
                points_entry.insert(0, str(event_score_data.get("points", "")))


    # Bind update function to team selection change
    selected_team_var.trace_add("write", update_input_fields)
    update_input_fields() # Initial call to set up fields for the first team

    button_frame_record = tk.Frame(popup)
    button_frame_record.pack(pady=10)

    def save_team_score():
        # Ensure entries are not None before trying to get their value
        if wins_entry is None and points_entry is None: # This should ideally not happen if update_input_fields ran
            score_msg_label.config(text="Error: Input fields not initialised. Please re-open.", fg="red")
            return

        team = selected_team_var.get()
        current_event = selected_event_for_tournament
        event_type = event_details[current_event]["type"]
        score_data = {}
        total_event_points = 0

        score_msg_label.config(text="", fg="red") # Reset message

        if event_type == "Tournament":
            wins_str = wins_entry.get().strip()
            losses_str = losses_entry.get().strip()

            if not wins_str or not losses_str:
                score_msg_label.config(text="Matches Won/Lost cannot be empty.", fg="red")
                return
            try:
                wins = int(wins_str)
                losses = int(losses_str)
                if wins < 0 or losses < 0:
                    score_msg_label.config(text="Matches Won/Lost cannot be negative.", fg="red")
                    return
            except ValueError:
                score_msg_label.config(text="Matches Won/Lost must be numbers.", fg="red")
                return

            total_event_points = (wins * 3) + (losses * 1)
            score_data = {"wins": wins, "losses": losses, "points": total_event_points}
            msg = f"Saved: {team} - {current_event} (Wins: {wins}, Losses: {losses}, Points: {total_event_points})"

        elif event_type == "Elimination":
            points_str = points_entry.get().strip()
            if not points_str:
                score_msg_label.config(text="Final Points cannot be empty.", fg="red")
                return
            try:
                total_event_points = int(points_str)
                if total_event_points < 0:
                    score_msg_label.config(text="Points cannot be negative.", fg="red")
                    return
            except ValueError:
                score_msg_label.config(text="Points must be a number.", fg="red")
                return
            score_data = {"points": total_event_points}
            msg = f"Saved: {team} - {current_event} (Points: {total_event_points})"

        # Confirm overwrite if score already exists for this event
        if current_event in teams_data[team]["event_scores"]:
            confirm = messagebox.askyesno("Confirm Overwrite",
                                           f"'{team}' already has a score for '{current_event}'. Overwrite?")
            if not confirm:
                score_msg_label.config(text="Score not saved (overwrite cancelled).", fg="blue")
                return

        teams_data[team]["event_scores"][current_event] = score_data
        teams_data[team]["total_score"] = total_event_points # Total score is just points from this single event

        score_msg_label.config(text=msg, fg="green")
        # Clear entries after saving
        if wins_entry: wins_entry.delete(0, tk.END)
        if losses_entry: losses_entry.delete(0, tk.END)
        if points_entry: points_entry.delete(0, tk.END)
        save_data()

    tk.Button(button_frame_record, text="Save Team Score", command=save_team_score).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame_record, text="Exit", command=popup.destroy).pack(side=tk.LEFT, padx=5)


def export_leaderboard_to_csv(popup_window, current_event):
    """Exports the current leaderboard data to a CSV file."""
    if not teams_data:
        messagebox.showinfo("Export CSV", "No teams or scores to export.")
        return

    # Sort teams by total score in descending order
    sorted_teams = sorted(teams_data.items(), key=lambda item: item[1]["total_score"], reverse=True)

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save Leaderboard as CSV",
        initialfile="tournament_leaderboard.csv"
    )

    if not file_path:
        # User cancelled the save dialog
        return

    try:
        with open(file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Define headers based on event type
            headers = ["Rank", "Team Name", "Score"]
            is_tournament_event = False
            if current_event and event_details[current_event]["type"] == "Tournament":
                headers.append("Wins/Losses")
                is_tournament_event = True
            
            csv_writer.writerow(headers)

            display_rank_counter = 1
            for team_name, data in sorted_teams:
                current_event_score_info = data["event_scores"].get(current_event, {})
                team_score = current_event_score_info.get("points", 0)

                row = [display_rank_counter, team_name, team_score]
                if is_tournament_event:
                    wins = current_event_score_info.get("wins", 0)
                    losses = current_event_score_info.get("losses", 0)
                    row.append(f"{wins}/{losses}")
                
                csv_writer.writerow(row)
                display_rank_counter += 1
        
        messagebox.showinfo("Export CSV", f"Leaderboard successfully exported to:\n{file_path}")
        status_label.config(text=f"Leaderboard exported to {os.path.basename(file_path)}", fg="green")
    except Exception as e:
        messagebox.showerror("Export CSV Error", f"Failed to export leaderboard:\n{e}")
        status_label.config(text=f"Error exporting leaderboard: {e}", fg="red")


def show_leaderboard_popup():
    popup = tk.Toplevel(root)
    popup.title("Overall Leaderboard")
    
    # Set the popup to fullscreen
    popup.attributes('-fullscreen', True)
    # Allow escaping fullscreen for the popup
    popup.bind("<Escape>", lambda e: popup.attributes('-fullscreen', False))

    if not teams_data:
        tk.Label(popup, text="No teams or scores recorded yet.").pack()
        tk.Button(popup, text="Exit", command=popup.destroy).pack(pady=10) # Exit button for empty state
        return

    # Sort teams by total score in descending order
    sorted_teams = sorted(teams_data.items(), key=lambda item: item[1]["total_score"], reverse=True)

    tk.Label(popup, text="Tournament Leaderboard:", font=("Arial", 14, "bold")).pack(pady=10)
    if selected_event_for_tournament:
        tk.Label(popup, text=f"For Event: {selected_event_for_tournament}", font=("Arial", 10)).pack(pady=2)

    leaderboard_frame = tk.Frame(popup)
    leaderboard_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Headers
    tk.Label(leaderboard_frame, text="Rank", font=("Arial", 10, "bold"), anchor="w").grid(row=0, column=0, padx=5, pady=2)
    tk.Label(leaderboard_frame, text="Team Name", font=("Arial", 10, "bold"), anchor="w").grid(row=0, column=1, padx=5, pady=2)
    tk.Label(leaderboard_frame, text="Score", font=("Arial", 10, "bold"), anchor="e").grid(row=0, column=2, padx=5, pady=2)

    # Conditionally add "Wins/Losses" header if it's a Tournament event
    if selected_event_for_tournament and event_details[selected_event_for_tournament]["type"] == "Tournament":
        tk.Label(leaderboard_frame, text="W/L", font=("Arial", 10, "bold"), anchor="e").grid(row=0, column=3, padx=5, pady=2)


    display_rank_counter = 1
    for team_name, data in sorted_teams:
        current_event_score_info = data["event_scores"].get(selected_event_for_tournament, {})
        team_score = current_event_score_info.get("points", 0) # Get score for the selected event

        display_text_extra = ""
        # Only show wins/losses if it's the selected tournament event type
        if selected_event_for_tournament and event_details[selected_event_for_tournament]["type"] == "Tournament":
            wins = current_event_score_info.get("wins", 0)
            losses = current_event_score_info.get("losses", 0)
            display_text_extra = f"{wins}/{losses}"

        tk.Label(leaderboard_frame, text=str(display_rank_counter), anchor="w").grid(row=display_rank_counter, column=0, padx=5, pady=2)
        tk.Label(leaderboard_frame, text=team_name, anchor="w").grid(row=display_rank_counter, column=1, padx=5, pady=2)
        tk.Label(leaderboard_frame, text=str(team_score), anchor="e").grid(row=display_rank_counter, column=2, padx=5, pady=2)
        if display_text_extra: # Only display the extra column if it's applicable
            tk.Label(leaderboard_frame, text=display_text_extra, anchor="e").grid(row=display_rank_counter, column=3, padx=5, pady=2)
        display_rank_counter += 1
    
    # Buttons for leaderboard
    leaderboard_button_frame = tk.Frame(popup)
    leaderboard_button_frame.pack(pady=10)
    tk.Button(leaderboard_button_frame, text="Export to CSV", command=lambda: export_leaderboard_to_csv(popup, selected_event_for_tournament)).pack(side=tk.LEFT, padx=5)
    tk.Button(leaderboard_button_frame, text="Exit", command=popup.destroy).pack(side=tk.LEFT, padx=5)


# --- Main Application Window Setup ---
root = tk.Tk()
root.title("Tournament Scoring System")
root.attributes('-fullscreen', True)  # Enable fullscreen

# Optional: Escape to exit fullscreen
root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))

# --- Top: Explanation Text ---
explanation_label = tk.Label(root, text=(
    "This application manages a team-based tournament.\n"
    "Phase 1: Create and manage teams.\n"
    "Phase 2: Select the main event and record scores.\n"
    "Phase 3: View rankings based on scores entered.\n"
    "Use Save to back up progress or Exit to quit the application."
), font=("Arial", 12), justify="center", pady=10)
explanation_label.pack(pady=20)

# --- Status & Current Event Info ---
status_label = tk.Label(root, text="", fg="blue", font=("Arial", 10))
status_label.pack(pady=5)

current_event_label = tk.Label(root, text="Current Event: Not Selected", font=("Arial", 10, "italic"))
current_event_label.pack(pady=5)

load_data()

# --- Main Button Area Container ---
button_container = tk.Frame(root)
button_container.pack(side="bottom", pady=40)

# --- Phase 1: Team Setup ---
phase1 = tk.LabelFrame(button_container, text="Phase 1: Teams", padx=10, pady=10)
phase1.pack(side="left", padx=30)
tk.Button(phase1, text="Create Team Data", command=initialise_teams).pack(pady=5)
tk.Button(phase1, text="Manage Teams & Members", command=manage_teams_popup).pack(pady=5)

# --- Phase 2: Event & Scores ---
phase2 = tk.LabelFrame(button_container, text="Phase 2: Event & Scores", padx=10, pady=10)
phase2.pack(side="left", padx=30)
tk.Button(phase2, text="View & Select Event", command=select_event_popup).pack(pady=5)
tk.Button(phase2, text="Record Team Scores", command=record_team_score_popup).pack(pady=5)

# --- Phase 3: Leaderboard ---
phase3 = tk.LabelFrame(button_container, text="Phase 3: Leaderboard", padx=10, pady=10)
phase3.pack(side="left", padx=30)
tk.Button(phase3, text="Show Overall Leaderboard", command=show_leaderboard_popup).pack(pady=15)

# --- Save & Exit Centered ---
bottom_controls = tk.Frame(root)
bottom_controls.pack(pady=10)
tk.Button(bottom_controls, text="Save Current Data", command=save_data).pack(side="left", padx=10)
tk.Button(bottom_controls, text="Exit Application", command=root.quit).pack(side="left", padx=10)

# Exit Confirmation
def on_closing():
    if messagebox.askyesno("Exit Application", "Do you want to save data before exiting?"):
        save_data()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()