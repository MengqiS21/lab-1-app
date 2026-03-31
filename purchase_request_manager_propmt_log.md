## AI Interaction Log — Purchase Request Manager
Tool: Cursor | Project: Purchase Request Manager (Streamlit)

### Interaction 1
Prompt: Build a Streamlit web app called "Purchase Request Manager" for a student program coordinator. The app has two roles: Student (submit requests) and Coordinator (review and manage all requests). Spec includes: student form fields (team number, CFO, supplier, item, quantity, unit price, purchase link, notes), coordinator dashboard with inline status updates and comments, summary tab by team, filter controls, CSV data persistence, and edge case handling.
Output: Generated app.py, requirements.txt, and README.md. Included CSV auto-creation, st.tabs() layout, password protection, inline status/comment editing, team summary tab, and filter controls.
First try? No. Multiple bugs required follow-up fixes: (1) Total price did not update live because st.form blocks re-runs; (2) empty coordinator_comment fields were read as float/NaN, crashing the data editor; (3) LinkColumn was incompatible with empty URLs. These were fixed in later prompts.

### Interaction 2
Prompt: Why can't I open the terminal? Also, do you think the data could come from an online real-time source like Google Forms instead of a local CSV? If so, can you create a mock CSV with these fields: Team number, CFO, Provider/Supplier, Quantity, Name of item, Price, Link to purchase, Notes, Approval from instructor (Y/N). Fictional data is fine.
Output: Diagnosed the terminal error (zsh: command not found: streamlit) as a Conda base environment vs. project .venv conflict, and provided two fix options. Explained how Google Sheets API integration could work as an alternative to CSV. Generated mock_requests.csv with fictional data matching the requested columns, and noted that column names differ from the main app's CSV schema.
First try? Yes for the terminal diagnosis and mock CSV. The Google Forms integration was explained conceptually only, not implemented.

### Interaction 3
Prompt: After clicking into Streamlit, I see this screen. How do I fix it? (Screenshot of Streamlit Community Cloud deploy prompt)
Output: Explained that the popup was a Streamlit Community Cloud deployment prompt, not a local error. Clarified that local use only requires running streamlit run app.py and visiting http://localhost:8501. Provided step-by-step instructions for GitHub-based cloud deployment if needed.
First try? Yes. This was an explanation/clarification prompt with no code changes needed.

### Interaction 4
Prompt: What is my current coordinator password? Is it coord2024?
Output: Confirmed the current password in app.py is coord2026 (not coord2024), and pointed to the exact line in the file.
First try? Yes.

### Interaction 5
Prompt: The total is not updating after input. Also, after submitting a request, the coordinator view shows an error.
Output: Fixed two bugs: (1) replaced st.form with a plain button so quantity and unit price trigger re-runs and the total updates live; (2) added fillna("") and str conversion in load_requests() so empty coordinator_comment fields no longer cause type errors in the data editor.
First try? No. This was a direct bug fix prompted by observed runtime errors.

### Interaction 6
Prompt: Now that there are no bugs, I want two improvements: (1) When the coordinator approves a request, the student side should receive an in-app notification. (2) Can the overall color style be changed to something light and fresh? The current black and red feels a bit too intense.
Output: Added a notifications.csv system: when a request is changed to Approved and saved, a notification is written for that team number. On the student tab, a "Team inbox" section lets students enter their team number to view and dismiss approval notifications. Also created .streamlit/config.toml with a light, muted green-gray color theme to replace the default dark styling.
First try? Yes. Both features were implemented as requested without requiring further correction.