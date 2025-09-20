import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright
from pop_users import click_first_group, open_group_gifts
from image_recognition import is_gift
from config import CFG

USERS_FILE = Path(CFG.get("USERS_FILE", "users.txt"))
SHOTS_DIR = Path(CFG.get("SHOTS_DIR", "shots"))
SHOTS_DIR.mkdir(parents=True, exist_ok=True)
CFG["SHOTS_DIR"] = SHOTS_DIR


async def highlight_bypass(page, max_wait_ms: int = 180000):
    """
    Wait automatically (no user input) until Telegram's search bar appears,
    which indicates login/verification is complete.

    - max_wait_ms: how long to wait in milliseconds (default 3 minutes).
    """
    selector = "div.input-search input.input-field-input"
    print("⚠️ Waiting for Telegram login/verification to complete (automatic)...")
    try:
        # wait_for_selector will return as soon as element is visible or raise on timeout
        await page.wait_for_selector(selector, state="visible", timeout=max_wait_ms)
        # small settle pause
        await asyncio.sleep(0.5)
        print("✅ Search bar detected — continuing automatically.")
        return True
    except Exception:
        print(f"❌ Timeout after {max_wait_ms/1000:.0f}s waiting for search bar.")
        return False



async def process_user(page, username: str):
    """
    Visit a user's profile in the group and take screenshots of gifts.
    """
    uname = username if username.startswith("@") else "@" + username
    print(f"\n🔍 Searching for {uname}")

    # Search for the user
    search_box = page.locator("div.input-search input.input-field-input")
    await search_box.fill(uname)
    await page.keyboard.press("Enter")
    await asyncio.sleep(1.5)

    profile_link = page.locator("a[href*='/'], div[role='link']").first
    if not await profile_link.is_visible():
        print(f"⚠️ Profile not found: {uname}")
        return False

    await profile_link.click()
    await asyncio.sleep(2)

    # Open Gifts tab via side panel
    if not await open_group_gifts(page):
        print(f"❌ Could not open Gifts tab for {uname}")
        return False

    # Collect gifts
    gift_images = page.locator("img")
    count = await gift_images.count()
    print(f"📦 Found {count} images in Gifts tab for {uname}")

    found_gift = False
    for i in range(count):
        safe_name = re.sub(r"[^a-zA-Z0-9]", "_", uname)
        path = SHOTS_DIR / f"{safe_name}_gift_{i}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        await gift_images.nth(i).screenshot(path=str(path))

        if is_gift(str(path)):
            print(f"🎁 Gift match detected for {uname} (image {i})")
            found_gift = True

    if not found_gift:
        print(f"❌ No matching gifts for {uname}")

    return found_gift


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()

        # Open Telegram Web
        await page.goto("https://web.telegram.org/k/")

        # Automatically wait for login/verification to finish (no Enter required)
        ok = await highlight_bypass(page, max_wait_ms=180000)  # adjust timeout if needed
        if not ok:
            print("Exiting because login/verification did not complete in time.")
            await browser.close()
            return

        # === Select group (first occurrence of given name in chat list) ===
        target_group = "ТРУСЫ РАЙЗА"   # <-- change to your target group name
        got_group = await click_first_group(page, target_group)
        if not got_group:
            print(f"❌ Could not find or click group '{target_group}'. Exiting.")
            await browser.close()
            return
        print(f"✅ Working inside group: {target_group}")

        # === Open side panel and Gifts tab for the group (optional) ===
        opened_gifts = await open_group_gifts(page)
        if not opened_gifts:
            print("⚠️ Gifts tab not opened — continuing anyway (per your flow).")

        # === Phase 1: (If you still need to collect usernames outside screenshots) ===
        # If you removed member scraping, ensure users.txt exists. If you still want to run
        # a collector, uncomment and use:
        # await collect_usernames_from_group(page, target_group)

        # Load usernames from USERS_FILE (must exist)
        if not USERS_FILE.exists():
            print("⚠️ users.txt not found — nothing to process. Exiting.")
            await browser.close()
            return

        with open(USERS_FILE, "r", encoding="utf8") as f:
            usernames = [line.strip() for line in f if line.strip()]

        print(f"\n📑 Loaded {len(usernames)} usernames from {USERS_FILE}")

        # === Phase 2: process each user sequentially ===
        for uname in usernames:
            try:
                await process_user(page, uname)
            except Exception as e:
                print(f"❌ Error processing {uname}: {e}")

        print("🏁 All done — closing browser.")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())