import asyncio
import re
from pathlib import Path

from playwright.async_api import async_playwright

from pop_users import collect_usernames_from_group
from image_recognition import is_gift
from config import CFG


# ensure USERS_FILE is defined (use your config or default)
USERS_FILE = Path(CFG.get("USERS_FILE", "users.txt"))

# ensure SHOTS_DIR exists
shots_dir = Path(CFG.get("SHOTS_DIR", "shots"))
shots_dir.mkdir(parents=True, exist_ok=True)
CFG["SHOTS_DIR"] = shots_dir


async def highlight_bypass(page):
    """
    Wait until Telegram's search widget (div.input-search > input.input-search-input)
    appears in the page — used as a reliable sign that login/verification completed.
    This will wait indefinitely until the selector is visible.
    """
    selector = "div.input-search input.input-search-input"
    print("\n⏸ Waiting for Telegram login/verification to complete...")
    print("   -> Please complete login/verification manually in the opened browser.")
    print("   -> The script will continue automatically once the search bar appears.\n")

    # Wait forever (timeout=0) until the search input is visible
    await page.wait_for_selector(selector, state="visible", timeout=0)

    # small pause to allow UI to settle
    await asyncio.sleep(0.5)
    print("✅ Search bar detected — login/verification complete, continuing...")


async def process_user(page, username: str):
    """
    Search for a username, open their profile, go to Gifts tab,
    and check each gift against gifts_ref/.
    """
    uname = username if username.startswith("@") else "@" + username
    print(f"\n🔍 Searching for {uname}")

    # Use new search widget selector
    search_selector = "div.input-search input.input-search-input"
    await page.wait_for_selector(search_selector, timeout=30000)
    search_input = page.locator(search_selector).first
    await search_input.click()
    await search_input.fill(uname)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1500)

    # Click first profile result
    profile_link = page.locator("a[href*='/'], div[role='link']").first
    if not await profile_link.is_visible():
        print(f"⚠️ No profile found for {uname}")
        return False
    await profile_link.click()
    await page.wait_for_timeout(2000)

    # === Open Gifts tab ===
    gifts_tab = page.locator("text=Gifts, text=Подарки").first
    if await gifts_tab.is_visible():
        await gifts_tab.click()
        await page.wait_for_timeout(1500)
    else:
        print(f"⚠️ No Gifts tab found for {uname}")
        return False

    # === Collect and check gifts ===
    gift_images = page.locator("img")
    count = await gift_images.count()
    print(f"📦 Found {count} images in Gifts tab for {uname}")

    found_gift = False
    for i in range(count):
        safe_name = re.sub(r"[^a-zA-Z0-9]", "_", uname)
        path = CFG["SHOTS_DIR"] / f"{safe_name}_gift_{i}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        await gift_images.nth(i).screenshot(path=str(path))

        if is_gift(str(path)):
            print(f"🎁 Gift match detected in {uname}'s Gifts tab (image {i})")
            found_gift = True

    if not found_gift:
        print(f"❌ No matching gifts for {uname}")

    return found_gift


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()

        # Go to Telegram Web
        await page.goto("https://web.telegram.org/k/")

        # Pause until user finishes login/verification
        await highlight_bypass(page)

        # === Phase 1: Collect usernames ===
        group_name = "Test Group"   # 🔹 change this to your real target group
        await collect_usernames_from_group(page, group_name)

        # Load usernames from file
        if not USERS_FILE.exists():
            print("⚠️ No users.txt found after Phase 1")
            await browser.close()
            return

        with open(USERS_FILE, "r", encoding="utf8") as f:
            usernames = [line.strip() for line in f if line.strip()]

        print(f"\n📑 Loaded {len(usernames)} usernames from {USERS_FILE}")

        # === Phase 2: Check gifts for each user ===
        for uname in usernames:
            try:
                await process_user(page, uname)
            except Exception as e:
                print(f"❌ Error processing {uname}: {e}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())