# Allplan Report Design – Guide

*[Deutsch](anleitung-de.md) · English*

This guide shows step by step how to set up the skill, create your workshop, have a first report of your own built, check it and open it in Allplan. You do not need any programming knowledge. The short version is in the [README](../README.en.md).

## 1. Overview

The skill turns your AI into a helper for designed Allplan reports. It contains:

- **allplan-report-design**: the knowledge for designing (what works in Allplan reports and what does not), a construction kit with the master report and six companion reports (seven templates per language in all, 81 building blocks), and the tools to build and look at reports.
- **allplan-report**: the basics for every Allplan report: how queries are built, how to look up attributes and how a report is checked.

**What you need**

| | |
|---|---|
| Allplan 2027 | to open the finished reports and for the preview on your computer |
| An AI with file access | GitHub Copilot in VS Code (agent mode), Claude Code or Codex. It must be allowed to read files and run commands. |
| Python 3.10 or newer | For building and checking, the Python of Allplan 2027 is enough, it is already there: `C:\Program Files\Allplan\Allplan 2027\Prg\Python\python.exe` |
| Only for two side tools: a Python of your own, 3.10 or newer | Saving PDF pages as images (`python -m pip install pymupdf pillow`) and the included tests (`python -m pip install pytest`). The Python of Allplan lacks PyMuPDF and pytest; Pillow is already there. Building, preview, the English version and checking do not need them. |

**Terms**

- **Skill**: a guide with tools that your AI reads before it starts working.
- **Project folder**: the folder you open in VS Code or in the terminal. The skill lives there.
- **Workshop**: a working folder of its own with the construction kit for reports. Finished reports are in its subfolder `out`.
- **Building block**: a finished section of a report, for example a chart. Each has an identifier such as `D040`. There are 81 blocks: 50 in the master, 31 in the six companion reports.
- **Teilbild**: the drawing file in Allplan that holds your model.

## 2. Set up the skill

### 2.1 Put the repo in place

Download the repo or copy it to a place with a short path, for example `C:\Allplan-Tools\allplan-report-design`. It stays there as a source. Copies go into your project folder.

### 2.2 Create the project folder

Create an empty folder with a short path, for example `C:\Projects\Reports`. This is your project folder.

### 2.3 Where the folders go

Copy the **contents** of the repo folder `skills\` into the skill folder of your tool. These are the two folders `allplan-report-design` and `allplan-report`.

| Tool | Target folder in the project folder |
|---|---|
| GitHub Copilot in VS Code | `.github\skills\` |
| Claude Code | `.claude\skills\` |
| Codex (coding tool from OpenAI) | `.agents\skills\` |

For **GitHub Copilot**, the project folder then looks like this:

```
C:\Projects\Reports\
└── .github\
    └── skills\
        ├── allplan-report-design\     ← with SKILL.md and further files
        └── allplan-report\            ← with SKILL.md, references, scripts
```

With Claude Code the top folder is `.claude`, with Codex `.agents`.

### 2.4 Step by step in Windows Explorer

Example GitHub Copilot, repo in `C:\Allplan-Tools\allplan-report-design`, project folder `C:\Projects\Reports`:

1. In the project folder, create a new folder `.github`. If Explorer does not accept a name with a dot at the start, type `.github.` (with a dot at the end). Windows removes the trailing dot by itself.
2. In `.github`, create a folder `skills`.
3. From the repo folder `skills`, copy the two folders `allplan-report-design` and `allplan-report` to `.github\skills\`.

The same for Claude Code and Codex, only with the target folder from 2.3.

### 2.5 Alternatively in PowerShell

First adjust the two paths, then run only the block for your tool:

```powershell
$repo    = "C:\Allplan-Tools\allplan-report-design"
$project = "C:\Projects\Reports"

# GitHub Copilot
New-Item -ItemType Directory -Force "$project\.github\skills" | Out-Null
Copy-Item "$repo\skills\*" "$project\.github\skills\" -Recurse -Force

# Claude Code
New-Item -ItemType Directory -Force "$project\.claude\skills" | Out-Null
Copy-Item "$repo\skills\*" "$project\.claude\skills\" -Recurse -Force

# Codex
New-Item -ItemType Directory -Force "$project\.agents\skills" | Out-Null
Copy-Item "$repo\skills\*" "$project\.agents\skills\" -Recurse -Force
```

### 2.6 Open the project folder in the tool

- **VS Code with GitHub Copilot:** *File → Open Folder…* and choose the project folder. If you created the folders while VS Code was open, reload once: `Ctrl+Shift+P`, then *Developer: Reload Window*. Choose **agent mode** in the Copilot chat.
- **Claude Code:** in the terminal, change to the project folder and start it:
  ```powershell
  cd C:\Projects\Reports
  claude
  ```
- **Codex:** in the terminal, change to the project folder and start `codex`.

### 2.7 Several tools in the same project folder

That works. GitHub Copilot also reads skills from `.claude\skills` and `.agents\skills`. If you use Copilot together with Claude Code or Codex, leave out `.github\skills`, otherwise Copilot sees the skill twice.

### 2.8 ChatGPT in the chat window

The plain chat window cannot read files in your folder and cannot run commands. The skill is meant for an AI that can. In the chat window you can upload `SKILL.md` and the `references\` folder as knowledge and have it write build scripts that you run yourself. **This has not been tried.**

> **Not tried:** Setting up Copilot, Codex and Claude Code with exactly this skill has not been tried on someone else's computer. The folders are the ones where these tools expect skills. If something does not work for you, report it through the [Issues](../../../issues).

## 3. Check that the AI sees the skill

Just ask a question that the skill can answer:

> "Which charts work in an Allplan report, and which do not?"

The AI should refer to the skill `allplan-report-design` and give a table or list from its knowledge. If it only answers in general terms, check the folder name (it must be exactly `allplan-report-design` and contain the file `SKILL.md` directly) and start a new session.

## 4. Create the workshop

The workshop is your working folder for reports. You can ask the AI:

> "Create the workshop in the folder reports and show me the master."

Before the first report is built, the AI asks you once about style, colors and font and recommends the house design (section "Design" in the README). Without this decision no script builds a report.

Or you run it yourself, here for Copilot in the project folder:

```powershell
python .github\skills\allplan-report-design\werkstatt_anlegen.py reports
```

The command copies the construction kit, tools and templates from the skill into the folder `reports` and creates the empty folder `out` there. It stops if `reports` already contains files. You work only in this copy; the skill itself stays unchanged.

`master\core.py` contains `VERFASSER = "W. Liffers"` (the author name). Change it to your own name before your first report of your own (or tell the AI). Otherwise every generated file carries that name.

The AI builds the viewer program for the preview by itself the first time. It uses the program files of Allplan 2027 for that. To do so, it starts a PowerShell script with the switch `-ExecutionPolicy Bypass`. The AI asks first. This is expected and affects only this one script. After that it shows you the ten pages of the master as images.

## 5. Your first report

### 5.1 Word the task

Describe the report the way you would describe it to a colleague. The easiest way is ordering by identifier (see the README, section "Ordering by identifier"):

> "Build me a one-page report with K010, D040 and T020, titled 'Shell construction overview', without identifier lines."

You can also say what you want to see without identifiers: "A chart of the largest parts and a key figure for the total volume." The AI looks for matching blocks in the master and tells you their identifiers.

Stacking by identifier applies to the 50 master blocks. The 31 blocks of the companion reports have a query of their own and are built together with their report. If you name such an identifier when stacking, `build_auswahl.py` tells you so by name.

For the companion reports reinforcement, layout list and lists, plain sentences are enough:

> "Build me a reinforcement overview for this drawing file."
>
> "I need a part list per kind, each kind on its own page, with a QR code."
>
> "Show me what is still missing on my plans."

For a new wish, the AI first looks in its list "wish → way" (60 entries with the verdict "works", "works with a trick" or "does not work" and the way to get there). If something does not work, it tells you honestly.

### 5.2 Answer questions

The AI asks only what it cannot assume safely: for example whether demolition parts count or which quantities you want to see. Answer briefly. Everything it assumes, it tells you at the end.

### 5.3 Look at the result

After building, the file is in `out\`. The AI shows you a preview image. It is made without Allplan from sample data and shows layout and charts. The numbers are therefore sample numbers, not those of your model. Look at the image closely and say what should be different, for example "The heading is too long" or "Add D030 as well".

### 5.4 Changes and other language

| Goal | Example |
|---|---|
| Change a block | "I need D040, but with the ten largest rooms instead of parts." |
| Add a block | "Add M020 as well." |
| English version | "Turn it into the English version." (file in `out\eng\`) |

If a change needs data that the report does not query yet, the AI extends the query. It may then ask you to output a small probe report from Allplan as an Excel file. From that it makes new sample data.

**English version of a report of your own.** The AI enters the new texts of the report into the table `master\sprache\en\eigene.json` with `python master\sprache.py --sammeln out\<file>.rdlc` (each with the value `null`) and fills them in English. `python master\sprache.py --offen out\<file>.rdlc` must then show 0. After that, `python master\sprache.py --en out\<file>.rdlc` creates the file in `out\eng\`. Without a file name, `--en` translates all reports in `out\` whose name does not start with `_`.

## 6. Checking

### 6.1 The check line

Tell the AI: "Check the report and tell me what I should look at in Allplan." It checks the file with the skill `allplan-report` and gives you the check line word for word:

```
AMPEL: GRUEN | validate_rdlc | 1 Dateien, 0 Fehler, 0 Warnungen
```

- **GRUEN** (green): no findings.
- **ORANGE**: notes only. The AI explains each one. The report is usable. Two templates report one note each on purpose: wall finishes "table wider than body" (only one of three column widths is ever visible) and room elevations "RepeatOnNewPage missing" (the first row is a heading, not a column header).
- **ROT** (red): errors. The AI fixes them before it hands you the file.

The check on the computer does not know Allplan. It finds errors in how the file is built, but not whether the numbers fit your model. One of the rules is that elements must not overlap: in the Allplan report window one of them would otherwise be pushed away (warning W28). PDF and preview do not show this. Two more window rules are in the skill, without a check rule: a hidden field belongs in a container of its own across the full width, and small type needs 10 % width reserve, because the window sets it 3 to 8 % wider than the PDF.

### 6.2 The list for Allplan

You also get a list of what to look at in Allplan, for example:

- Does the number of rows match what you see in the model?
- Are the totals right?
- Do images and umlauts show correctly?
- For reports with interaction: the controls, expanding and sorting in the report window were checked first-hand and work. The click into the model (zoom to the part) is **not secured**: in the window that was opened for testing it had no effect, and it is not checked through Allplan's "Reports" command. Do not rely on it.

Until you report back what you saw, the report counts as **not checked in Allplan**.

## 7. Open it in Allplan

1. Copy the file from `out\` into the office folder of Allplan, into a folder of your own: `C:\allplandaten\2027\Std\Reports\deu\My reports\`. English reports go to `...\Reports\eng\My reports\`. This is the default path; with a different data path, adjust accordingly.
2. In Allplan, call the function **Reports** and choose the template.
3. Apply the report to the project and check it (list from 6.2).
4. If something differs, tell the AI exactly that, for example "Two columns are missing on the 1st floor".

The templates under `C:\ProgramData\Nemetschek\Allplan\2027\Etc\Reports` belong to Allplan. Do not put anything there and do not change anything.

In large projects, the output takes minutes. Wait, even if Allplan says "not responding" in between. In the report window, the master needs 22 to 24 seconds until the first page, further pages 5 to 15 seconds.

## 8. The finished templates without an AI

The folders `vorlagen\deu` and `vorlagen\eng` contain the finished reports. Copy the files of one language folder into the office folder as in section 7. What each template needs is in `vorlagen\README.md` and in the README.

The seven templates per language (German / English) and what each needs:

| Template | Needs |
|---|---|
| Report Master / Report Master | a drawing file with the parts |
| Report Master Grundriss / … Floor plan | a drawing file with parts and rooms |
| Report Master Raum-Abwicklung / … Room elevations | rooms **and** a drawing file with the elevation drawings, both together; without the drawing file with the rooms, the room cards stay empty |
| Report Master Wandbeläge / … Wall finishes | rooms with room finishes |
| Report Master Bewehrung / … Reinforcement | a drawing file with reinforcement |
| Report Master Planliste / … Layout list | a project with plans (no drawing file) |
| Report Master Listen / … Lists | a drawing file with the parts |

Example PDFs are in `beispiel\deu` and `beispiel\eng`. The PDFs for the layout list and the wall finishes are **preview with sample data, not from Allplan**; in Allplan, both were output on real projects and looked at. `beispiel\eng` also holds `Overview_Master.pdf` (in `beispiel\deu`: `Uebersicht_Master.pdf`) with all ten master pages on one sheet.

## 9. Update and remove

- **New version of the skill:** delete the folder `allplan-report-design` in the skill folder and copy it again from the new repo state. Your reports in `reports\out\` stay untouched. You bring the workshop itself to the new state with `python <skill folder>\werkstatt_anlegen.py reports --aktualisieren` (`<skill folder>` is `allplan-report-design` in the skill folder of your tool). It replaces only files you have not changed yourself; changed files stay, and the new version lies next to them as `.neu`.
- **Remove:** delete the folders `allplan-report-design` and `allplan-report` in the skill folder. The workshop is an ordinary folder and can simply be deleted.

## 10. Common problems

| Problem | Solution |
|---|---|
| The AI does not know the skill | Compare the folder names with section 2.3. The folder must be called `allplan-report-design` and contain the `SKILL.md` directly. Reload VS Code or start a new session. In Copilot, **agent mode** must be active. |
| Explorer will not create the folder `.github` | Enter `.github.` (dot at the end) or use PowerShell (section 2.5). |
| `python` is not found | Tell the AI to use the Python of Allplan: `C:\Program Files\Allplan\Allplan 2027\Prg\Python\python.exe`. |
| The preview cannot be created | The viewer program needs the program files of Allplan 2027. If Allplan is installed elsewhere, tell the AI the folder. |
| `werkstatt_anlegen.py` stops | The target folder is not empty. Use a new folder or, for an existing workshop, the option `--aktualisieren`. |
| The check line is ROT | Ask the AI to fix the findings. |
| Report stays empty in Allplan | The queried attributes are not filled in the model, or the filter does not fit the parts. Describe to the AI which parts should appear. If the query returns no row at all, Allplan creates no report. |
| Report stays white in Allplan | The template contains something Allplan does not understand. Ask the AI to check the file with the skill `allplan-report`. |
| Report stays empty in the report window | A parameter has an invalid default. Allplan accepts only fixed defaults and fixed lists. Ask the AI to check the parameters. |
| Text in the report window is cut off or blocks have slipped | Elements in the report overlap, and the window pushes one of them away. PDF and preview do not show this. The check script reports it as warning W28; ask the AI to remove the overlap. |
| The Excel output of a layout list opens the window instead of a file | Plans and project data can only be output as PDF or Word through a report, not as Excel. Output the report as PDF or Word. |
| The room elevations show nothing | The report does not draw by itself. The drawing must be in the drawing file (see README, section "Room elevations"). |
| Umlauts appear as "?" | The file was not saved as UTF-8. Ask the AI to rewrite it as UTF-8 without BOM. |
