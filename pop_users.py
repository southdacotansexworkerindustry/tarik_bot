# pop_users.py
import asyncio

async def click_first_group(page, group_name: str):
    """
    Finds the first appearance of the given group_name in the chat list
    and clicks it.
    """
    print(f"🔍 Looking for group: {group_name}")
    for _ in range(20):
        group_item = page.locator(f"div.row-title span.peer-title-inner:text('{group_name}')")
        if await group_item.count() > 0 and await group_item.is_visible():
            await group_item.click()
            await asyncio.sleep(1.5)
            print(f"✅ Group '{group_name}' clicked")
            return True
        await asyncio.sleep(1)
    print(f"❌ Could not find group '{group_name}' in chat list")
    return False


async def open_group_gifts(page):
    """
    Opens the side panel of the currently selected group and clicks the Gifts tab.
    Sequence: group -> side panel button -> Gifts tab
    """
    # Step 1: Click avatar/title button to open side panel
    side_panel_attempts = 0
    while side_panel_attempts < 20:
        header_button = page.locator(
            "div.chat-info div.person div.user-title span.peer-title-inner"
        )
        if await header_button.count() > 0 and await header_button.is_visible():
            await header_button.click()
            await asyncio.sleep(1.5)
            print("✅ Side panel opened")
            break
        await asyncio.sleep(1)
        side_panel_attempts += 1
    else:
        print("❌ Could not open side panel")
        return False

    # Step 2: Click Gifts tab
    gifts_tab_attempts = 0
    while gifts_tab_attempts < 20:
        gifts_tab = page.locator(
            "div.menu-horizontal-div-item span.i18n:text('Gifts')"
        )
        if await gifts_tab.count() > 0 and await gifts_tab.is_visible():
            await gifts_tab.click()
            await asyncio.sleep(1.5)
            print("✅ Gifts tab opened")
            return True
        await asyncio.sleep(1)
        gifts_tab_attempts += 1

    print("❌ Gifts tab not found")
    return False