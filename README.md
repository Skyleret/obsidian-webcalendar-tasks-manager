# obsidian-webcalendar-tasks-manager
Pull tasks from webcal:// calendar subscriptions and add them to your obsidian daily note

Here’s the optimized integration for your Obsidian-centric workflow, clearly distinguishing this from being an Obsidian plugin while acknowledging compatibility:

---
# iCalendar Task Sync for Obsidian

A Python script that syncs tasks from `.ics` calendars to **daily Markdown notes** compatible with Obsidian and the [obsidian-rollover-daily-todos](https://github.com/lumoe/obsidian-rollover-daily-todos) plugin.

## 🔌 Compatibility
- Input: **Any `.ics` calendar feed**
- Output: Markdown files in `YYYY/MMMM/YYYY-MM-DD.md` format
- Optimized for:  
  - [Obsidian](https://obsidian.md) (personal use)  
  - [obsidian-rollover-daily-todos](https://github.com/lumoe/obsidian-rollover-daily-todos) (MIT licensed)

⚠️ **Note**: This is *not* an Obsidian plugin. It generates files externally that Obsidian can read.

## 🛠️ Setup
1. Download the main.py code and put it in your obsidian vault
2. Configure your calendar URL in `main.py`:
   ```python
   CALENDAR_URL = "https://your-calendar-feed.ics" 
   ```
3. Install dependencies:
   ```bash
   pip install ics requests watchdog
   ```
4. Run:
   ```bash
   cd path-to-your-obsidian-vault
   python main.py  # Outputs to YOUR_VAULT/YYYY/MMMM/YYYY-MM-DD.md
   ```

## 🗂️ Obsidian Integration
Place the output files in your vault and use:
- The **rollover plugin** to manage unfinished tasks

## Privacy Note
This tool processes personal calendar data. By using it, you agree to:  
- Manually manage local files (`tasks.db`, `.md` files)  
- Not commit sensitive data to version control  

