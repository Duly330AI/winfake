#!/usr/bin/env python
"""
Automatisierter Test für Desktop-Verhalten
Testet: Desktop-Sichtbarkeit, Icons, Taskbar-Integration, Minimize
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

def test_desktop_visibility():
    """Test: Desktop und Icons bleiben sichtbar wenn Notepad öffnet"""
    print("=" * 60)
    print("TEST 1: Desktop Visibility")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    from desktop.desktop_area import DesktopWindow
    from core.session import Session
    
    desktop_win = DesktopWindow(Session('Milan'))
    desktop_win.show()
    
    # Initial State
    print("✓ Desktop created")
    print(f"  - Desktop area visible: {desktop_win.desktop.isVisible()}")
    print(f"  - Desktop has wallpaper: {desktop_win.desktop._wallpaper is not None}")
    print(f"  - Icons count: {len(desktop_win.desktop.icons)}")
    print(f"  - MDI visible: {desktop_win.mdi.isVisible()}")
    
    assert desktop_win.desktop.isVisible(), "Desktop should be visible"
    assert len(desktop_win.desktop.icons) > 0, "Desktop should have icons"
    assert not desktop_win.mdi.isVisible(), "MDI should be hidden initially"
    
    # Open Notepad
    print("\n✓ Opening Notepad...")
    desktop_win.open_notepad()
    
    # Process events
    app.processEvents()
    
    # Check after opening
    print(f"  - Desktop area visible: {desktop_win.desktop.isVisible()}")
    print(f"  - Icons visible: {desktop_win.desktop.icons[0].isVisible() if desktop_win.desktop.icons else False}")
    print(f"  - MDI visible: {desktop_win.mdi.isVisible()}")
    print(f"  - Subwindows count: {len(desktop_win.mdi.subWindowList())}")
    print(f"  - Taskbar buttons count: {len(desktop_win.taskbar_buttons)}")
    
    assert desktop_win.desktop.isVisible(), "❌ FAIL: Desktop should remain visible"
    assert desktop_win.desktop.icons[0].isVisible(), "❌ FAIL: Icons should remain visible"
    assert desktop_win.mdi.isVisible(), "MDI should be visible when window open"
    assert len(desktop_win.mdi.subWindowList()) == 1, "Should have 1 subwindow"
    assert len(desktop_win.taskbar_buttons) == 1, "Should have 1 taskbar button"
    
    print("\n✅ PASS: Desktop and icons remain visible")
    
    # Cleanup
    desktop_win.close()
    return True

def test_minimize_behavior():
    """Test: Minimize versteckt Fenster (kein Qt Icon)"""
    print("\n" + "=" * 60)
    print("TEST 2: Minimize Behavior")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    from desktop.desktop_area import DesktopWindow
    from core.session import Session
    
    desktop_win = DesktopWindow(Session('Milan'))
    desktop_win.show()
    
    # Open Notepad
    desktop_win.open_notepad()
    app.processEvents()
    
    sub = desktop_win.mdi.subWindowList()[0]
    print("✓ Notepad opened")
    print(f"  - Subwindow visible: {sub.isVisible()}")
    print(f"  - Subwindow state: {sub.windowState()}")
    
    # Trigger minimize
    print("\n✓ Triggering minimize...")
    sub.showMinimized()  # Use showMinimized instead of setWindowState
    app.processEvents()
    
    # Wait a bit for event to propagate
    from PySide6.QtCore import QTimer
    import time
    time.sleep(0.1)
    app.processEvents()
    
    # Check state after minimize
    print(f"  - Subwindow visible after minimize: {sub.isVisible()}")
    print(f"  - Subwindow state: {sub.windowState()}")
    
    # Window should be hidden (not minimized with Qt icon)
    assert not sub.isVisible(), "❌ FAIL: Window should be hidden after minimize"
    assert sub.windowState() == Qt.WindowNoState, "❌ FAIL: Window state should be NoState"
    
    print("\n✅ PASS: Window hidden on minimize (no Qt icon)")
    
    # Cleanup
    desktop_win.close()
    return True

def test_taskbar_integration():
    """Test: Taskbar button erscheint und funktioniert"""
    print("\n" + "=" * 60)
    print("TEST 3: Taskbar Integration")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    from desktop.desktop_area import DesktopWindow
    from core.session import Session
    
    desktop_win = DesktopWindow(Session('Milan'))
    desktop_win.show()
    
    # Open Notepad
    desktop_win.open_notepad()
    app.processEvents()
    
    sub = desktop_win.mdi.subWindowList()[0]
    
    print("✓ Notepad opened")
    print(f"  - Taskbar buttons: {len(desktop_win.taskbar_buttons)}")
    
    assert len(desktop_win.taskbar_buttons) == 1, "Should have 1 taskbar button"
    
    # Get button
    btn = desktop_win.taskbar_buttons[sub]
    print(f"  - Button text: {btn.text()}")
    print(f"  - Button visible: {btn.isVisible()}")
    
    # Click button to minimize
    print("\n✓ Clicking taskbar button (should minimize)...")
    btn.click()
    app.processEvents()
    
    print(f"  - Window visible after click: {sub.isVisible()}")
    assert not sub.isVisible(), "Window should be hidden after button click"
    
    # Click again to restore
    print("\n✓ Clicking taskbar button again (should restore)...")
    btn.click()
    app.processEvents()
    
    print(f"  - Window visible after restore: {sub.isVisible()}")
    assert sub.isVisible(), "Window should be visible after restore"
    
    print("\n✅ PASS: Taskbar integration works")
    
    # Cleanup
    desktop_win.close()
    return True

def test_close_removes_button():
    """Test: Schließen entfernt Taskbar-Button"""
    print("\n" + "=" * 60)
    print("TEST 4: Close Window")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    from desktop.desktop_area import DesktopWindow
    from core.session import Session
    
    desktop_win = DesktopWindow(Session('Milan'))
    desktop_win.show()
    
    # Open Notepad
    desktop_win.open_notepad()
    app.processEvents()
    
    print("✓ Notepad opened")
    print(f"  - Taskbar buttons: {len(desktop_win.taskbar_buttons)}")
    
    # Close window
    sub = desktop_win.mdi.subWindowList()[0]
    print("\n✓ Closing window...")
    sub.close()
    
    # Wait for cleanup
    import time
    time.sleep(0.2)
    app.processEvents()
    time.sleep(0.1)
    app.processEvents()
    
    print(f"  - Subwindows count: {len(desktop_win.mdi.subWindowList())}")
    print(f"  - Taskbar buttons count: {len(desktop_win.taskbar_buttons)}")
    print(f"  - MDI visible: {desktop_win.mdi.isVisible()}")
    
    assert len(desktop_win.mdi.subWindowList()) == 0, "Should have no subwindows"
    assert len(desktop_win.taskbar_buttons) == 0, "Should have no taskbar buttons"
    assert not desktop_win.mdi.isVisible(), "MDI should be hidden when no windows"
    
    print("\n✅ PASS: Close removes button and hides MDI")
    
    # Cleanup
    desktop_win.close()
    return True

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "WINFAKE DESKTOP BEHAVIOR TESTS" + " " * 17 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    tests = [
        ("Desktop Visibility", test_desktop_visibility),
        ("Minimize Behavior", test_minimize_behavior),
        ("Taskbar Integration", test_taskbar_integration),
        ("Close Window", test_close_removes_button),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, True, None))
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            results.append((name, False, str(e)))
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append((name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed, error in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"       {error}")
    
    passed_count = sum(1 for _, p, _ in results if p)
    total_count = len(results)
    
    print()
    print(f"Results: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.0f}%)")
    print("=" * 60)
    
    return 0 if passed_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())
