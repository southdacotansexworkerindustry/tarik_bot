# tarik_bot

This project automates the collection of Telegram usernames from a group and checks each user's **Gifts tab** against a folder of reference gift images (`gifts_ref`). It uses **Playwright** for web automation and **OpenCV** for image recognition.

---

## Features

1. **Collect usernames** from a Telegram group.
2. **Visit user profiles** and open their Gifts tab.
3. **Compare gift images** with a reference folder to detect specific gifts.
4. Saves **screenshots** of gifts to `shots/`.
5. Saves collected usernames to `users.txt`.

6. 
## Project Structure

tarik_bot/
├── main.py # Main script: Phase 1 (collect users) + Phase 2 (check gifts)
├── pop_users.py # Phase 1: Collect usernames from a Telegram group
├── image_recognition.py # Image matching logic using OpenCV
├── config.py # Paths and configuration variables
├── gifts_ref/ # Folder containing reference gift images
├── shots/ # Folder where screenshots of gifts are saved
├── users.txt # Output of collected usernames
└── venv/ # Python virtual environment


---

## Requirements

- Python 3.12+  
- Playwright (`pip install playwright`)  
- OpenCV (`pip install opencv-contrib-python`)  
- FS-extra, pathlib (standard in Python 3.12+)  

main.py
│
├─> Launch Playwright browser
│
├─> Open Telegram Web (https://web.telegram.org/k/)
│      │
│      └─> Wait for user to complete login/verification
│
├─> Click first group (pop_users.click_first_group)
│      │
│      └─> Finds group by name in chat list
│
├─> Open Gifts tab (pop_users.open_group_gifts)
│      │
│      └─> Clicks group header → opens side panel → selects Gifts tab
│
├─> Load usernames from users.txt
│
└─> For each username:
       │
       └─> process_user(page, username)
              │
              ├─> Search user in Telegram search bar
              │
              ├─> Click user profile
              │
              ├─> Open Gifts tab (already done via side panel)
              │
              ├─> Take screenshots of all gift images
              │
              └─> Check each screenshot against gifts_ref folder using image_recognition.is_gift
