import asyncio
from playwright.async_api import async_playwright
import os

USERS_FILE = "users.txt"

async def collect_usernames_from_group(page, group_name: str):
    """
    Opens a Telegram group, scrapes visible usernames,
    and saves them into users.txt
    """
    print(f"🔍 Opening group: {group_name}")

    # Focus search input
    await page.click("aside input[placeholder*='earch']")
    await page.fill("aside input[placeholder*='earch']", group_name)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1000)

    # Select first search result
    await page.keyboard.press("ArrowDown")
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1500)

    # Open group profile panel (header click)
    await page.click("header")
    await page.wait_for_timeout(1000)

    # Try opening the Members tab if it exists
    members_tab = await page.locator("text=Members").first
    if await members_tab.is_visible():
        await members_tab.click()
        await page.wait_for_timeout(1000)

    usernames = set()
    member_panel = page.locator("section")

    # Scroll through the member list several times
    for _ in range(15):
        await member_panel.evaluate("el => el.scrollBy(0, el.scrollHeight)")
        await page.wait_for_timeout(500)

        found = await page.locator("text=@").all_inner_texts()
        for t in found:
            parts = [w for w in t.split() if w.startswith("@")]
            usernames.update(parts)

    # Save usernames to file
    with open(USERS_FILE, "w", encoding="utf8") as f:
        for u in sorted(usernames):
            f.write(u + "\n")

    print(f"✅ Collected {len(usernames)} usernames into {USERS_FILE}")


async def run_pop_users(group_name: str):
    """
    Entry point for collecting usernames.
    Opens Telegram Web and runs collection.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="user_data",
            headless=False,
        )
        page = await browser.new_page()
        await page.goto("https://web.telegram.org/k/")

        await collect_usernames_from_group(page, group_name)

        # Leave browser open so session persists
        print("🖥️ Leaving browser open (user_data saved).")
        # await browser.close()  # uncomment if you want it to close automatically


if __name__ == "__main__":
    group = input("Enter Telegram group name to collect from: ")
    asyncio.run(run_pop_users(group))