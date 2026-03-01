# How to Save Code in GitHub

Follow these steps every time you want to save your code to GitHub.

---

## Step 1: Open a Terminal in Your Project Folder

1. Open **VS Code**
2. Go to the top menu: **Terminal → New Terminal**
3. Make sure you are in the `quincy` folder. You should see a path like:
   ```
   C:\Users\Quincy\source\repos\quincy
   ```

---

## Step 2: Check What Files Changed

Run this command to see what files you've added or changed:

```bash
git status
```

Files in **red** have changes that haven't been saved yet.

---

## Step 3: Stage Your Changes

Tell Git which files you want to save. To add everything at once:

```bash
git add .
```

Or to add just one specific file:

```bash
git add projects/flappy_bird.py
```

Run `git status` again — the files should now be **green**.

---

## Step 4: Commit Your Changes

A commit is like a save point. Write a short message describing what you changed:

```bash
git commit -m "describe what you changed here"
```

**Examples:**
```bash
git commit -m "added double jump to geometry dash"
git commit -m "fixed bug in flappy bird score"
git commit -m "created new bow battle level"
```

---

## Step 5: Push to GitHub

Upload your commit to GitHub so it's saved online:

```bash
git push
```

That's it! Your code is now saved on GitHub at:
https://github.com/QuincyHPaaaina/quincy

---

## Quick Reference (All 3 Commands Together)

```bash
git add .
git commit -m "your message here"
git push
```

---

## Tips

- **Commit often** — save after every feature or fix, not just at the end
- **Write clear messages** — future you will thank you
- **Never commit highscore files** — they are already blocked by `.gitignore`
- To see your full commit history, run: `git log --oneline`
