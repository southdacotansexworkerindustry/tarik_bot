import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright

from pop_users import collect_usernames_from_group
from image_recognition import is_gift

USERS_FILE = "users.txt"

# === Config (was in config.py) ===
BASE_DIR = Path(__file__).resolve().parent
SHOTS_DIR = BASE_DIR / "shots"       # where screenshots will be saved
GIFTS_REF = BASE_DIR / "gifts_ref"   # folder with reference gift images

SHOTS_DIR.mkdir(parents=True, exist_ok=True)
GIFTS_REF.mkdir(parents=True, exist_ok=True)

CFG = {
    "BASE_DIR": BASE_DIR,
    "SHOTS_DIR": SHOTS_DIR,
    "GIFTS_REF": GIFTS_REF,
}


async def process_user(page, username: str):
    """
    Search for a username, open their profile, go to Gifts tab,
    and check each gift against gifts_ref/.
    """
    uname = username if username.startswith("@") else "@" + username
    print(f"\n🔍 Searching for {uname}")

    # Focus search box
    await page.click("aside input[placeholder*='earch']")
    await page.fill("aside input[placeholder*='earch']", uname)
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
        await gift_images.nth(i).screenshot(path=path)

        if is_gift(str(path)):
            print(f"🎁 Gift match detected in {uname}'s Gifts tab (image {i})")
            found_gift = True

    if not found_gift:
        print(f"❌ No matching gifts for {uname}")

    return found_gift


async def main():
    """
    Phase 1: Collect usernames from a Telegram group into users.txt
    Phase 2: Visit each user profile and check gifts against gifts_ref
    """
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()

        # === Phase 1: Collect usernames ===
        group_name = "Test Group"   # 🔹 change to your target group name
        await collect_usernames_from_group(page, group_name)

        # Load usernames from file
        if not Path(USERS_FILE).exists():
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