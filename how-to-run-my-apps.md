# How to Run My Apps Without Claude

You can run all your apps directly from VS Code or File Explorer — no Claude needed!

---

## One-Time Setup (Do This First)

Most of the Python games use a library called **pygame**. You only need to install it once.

1. Open **VS Code**
2. Open a terminal: **Terminal → New Terminal**
3. Run this command:
   ```bash
   pip install pygame
   ```
4. Wait for it to finish. You should see: `Successfully installed pygame-...`

That's it! You won't need to do this again.

---

## How to Run Python Games

These games need Python to run:

| Game | File |
|------|------|
| Flappy Bird | `projects/flappy_bird.py` |
| Geometry Dash | `projects/geometry_dash.py` |
| Factory Runner | `projects/factory_runner.py` |
| Pi Quiz | `projects/pi_quiz.py` |
| Bald With Hair | `projects/bald_with_hair.py` |

### Option A: Run from VS Code (Easiest)

1. Open **VS Code**
2. In the left sidebar, open your `projects` folder
3. Click on the game file you want to open (e.g. `flappy_bird.py`)
4. Click the **Run** button (the triangle ▷ in the top right corner)
5. The game window will pop up!

### Option B: Run from the Terminal

1. Open a terminal in VS Code: **Terminal → New Terminal**
2. Type this command (swap the filename for the game you want):
   ```bash
   python projects/flappy_bird.py
   ```

   Other examples:
   ```bash
   python projects/geometry_dash.py
   python projects/factory_runner.py
   python projects/pi_quiz.py
   python projects/bald_with_hair.py
   ```

### Option C: Double-Click from File Explorer

1. Open **File Explorer**
2. Navigate to: `C:\Users\Quincy\source\repos\quincy\projects`
3. Right-click the `.py` file you want
4. Click **Open with → Python**

> If "Python" doesn't show up, choose **Choose another app** and find Python in the list.

---

## How to Run HTML Games

These games run in your web browser — no Python needed:

| Game | File |
|------|------|
| Bow Battle | `projects/bow_battle.html` |
| Doodle Jump | `projects/doodle_jump.html` |

### Steps:

1. Open **File Explorer**
2. Navigate to: `C:\Users\Quincy\source\repos\quincy\projects`
3. Double-click the `.html` file
4. It will open in your default browser and start immediately!

---

## Troubleshooting

**"No module named pygame"**
→ Run `pip install pygame` in the terminal and try again.

**The game window opens but closes right away**
→ Run the game from the terminal instead of double-clicking, so you can see any error messages.

**"Python was not found"**
→ Python might not be set in your PATH. Try opening VS Code, opening a terminal there, and running with `python filename.py`.

**The game is running but I can't see the window**
→ Check your taskbar at the bottom — the window might be hiding behind other apps.
