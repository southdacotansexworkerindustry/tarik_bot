import asyncio
from pathlib import Path

from config import CFG


async def collect_usernames_from_group(page, group_name: str):
    """
    Search for a Telegram group, open it, collect usernames from members list,
    and save them into users.txt.
    """

    # Use new search widget selector
    search_selector = "div.input-search input.input-search-input"
    await page.wait_for_selector(search_selector, timeout=60000)

    search_input = page.locator(search_selector).first
    await search_input.click()
    await search_input.fill(group_name)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1500)

    # Click on the first group result
    group_result = page.locator("a[href*='/']").first
    if not await group_result.is_visible():
        print(f"⚠️ Group '{group_name}' not found")
        return
    await group_result.click()
    await page.wait_for_timeout(2000)

    # Open members list
    members_button = page.locator("text=Members, text=Участники").first
    if await members_button.is_visible():
        await members_button.click()
        await page.wait_for_timeout(2000)
    else:
        print("⚠️ No members list found in this group.")
        return

    # Scroll members panel to load more
    members_panel = page.locator("div[role='dialog']")
    for _ in range(10):
        await members_panel.evaluate("el => el.scrollBy(0, el.scrollHeight)")
        await page.wait_for_timeout(500)

    # Collect usernames
    usernames = set()
    name_nodes = page.locator("a[href^='https://t.me/']")
    count = await name_nodes.count()
    for i in range(count):
        href = await name_nodes.nth(i).get_attribute("href")
        if href and href.startswith("https://t.me/"):
            username = href.replace("https://t.me/", "").strip("/")
            if username:
                usernames.add(username)

    # Save to users.txt
    users_file = Path(CFG.get("USERS_FILE", "users.txt"))
    with open(users_file, "w", encoding="utf8") as f:
        for u in sorted(usernames):
            f.write(u + "\n")

    print(f"✅ Collected {len(usernames)} usernames into {users_file}")