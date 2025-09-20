import asyncio
from pathlib import Path

USERS_FILE = "users.txt"


async def collect_usernames_from_group(page, group_name: str):
    """
    Navigate to the group, open members, scroll, and collect usernames.
    Writes all usernames to users.txt.
    """
    print(f"🔍 Opening group: {group_name}")

    # --- Focus search bar in chats list ---
    search_container = page.locator("div.input-search input.input-field-input")
    await search_container.click()
    await search_container.fill(group_name)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1500)

    # --- Click first group in the results ---
    group_row = page.locator("div.row-title span.peer-title-inner").filter(has_text=group_name).first
    if not await group_row.is_visible():
        print(f"⚠️ Group '{group_name}' not found")
        return []
    await group_row.click()
    await page.wait_for_timeout(2000)

    # --- Open Members tab ---
    members_tab = page.locator("text=Members").first
    if await members_tab.is_visible():
        await members_tab.click()
        await page.wait_for_timeout(1000)
    else:
        print("⚠️ Members tab not found")
        return []

    # --- Scroll members panel and collect usernames ---
    usernames = set()
    member_panel = page.locator("section")  # panel containing members

    for _ in range(15):  # scroll multiple times
        await member_panel.evaluate("el => el.scrollBy(0, el.scrollHeight)")
        await page.wait_for_timeout(500)
        found = await page.locator("text=@").all_inner_texts()
        for t in found:
            parts = [w for w in t.split() if w.startswith("@")]
            usernames.update(parts)

    # --- Save usernames ---
    Path(USERS_FILE).write_text("\n".join(sorted(usernames)), encoding="utf8")
    print(f"✅ Collected {len(usernames)} usernames into {USERS_FILE}")
    return list(usernames)