# Qt native access-violation investigation

## Finding

The reproducible native failure was at Qt application teardown, not during login,
dashboard refresh, or image decoding. The existing GUI smoke test completed its
assertions and printed `1 passed`, but the Windows process intermittently exited
with `0xC0000005` (access violation). Its cleanup only closed the windows; it did
not destroy the top-level widgets while `QApplication` was still alive or flush
their queued `deleteLater()` events.

The UI has several parentless top-level windows: the login window, the main
window, and independently opened module-shell windows. Timers belong to their
respective widgets, and dashboard/module content widgets are adopted by layouts.
Those ownership relationships are valid while the application is running. The
failure was the unspecified destruction order at interpreter shutdown, when Qt
widgets and their timers could outlive `QApplication`.

## Inspection

- `dashboard_view.py`: its clock timer is parented to the dashboard; `refresh()`
  only updates the clock. Module buttons emit one signal with the captured module
  name. No refresh recursion or deleted-widget access was found.
- `main_window.py`: the dashboard is adopted by `QStackedWidget`; module windows
  are retained in `_open_windows`. Logout already used `deleteLater()` for module
  windows, but did not provide an orderly application-shutdown path.
- `module_shell.py`: each module shell owns its clock timer. The content widget
  is transferred into the shell's body layout, so Qt reparents it into the
  window's object tree.
- `support.py`: table population mutates the passed table synchronously; it has
  no timer or recursive refresh behavior. Its print-logo helper reads image bytes
  for an HTML data URI and does not create a `QPixmap`.
- Dashboard and module-shell `QPixmap` loads occur synchronously in widget
  constructors. The resolved asset is a valid 29,254-byte PNG at 154 x 180
  pixels; no invalid/null image or off-thread pixmap use was observed.

## Fix

`Shell.shutdown()` now closes and schedules deletion of the main, login, and
module-shell windows, then sends deferred-delete events and processes them before
the application object is released. `main()` invokes this cleanup in a `finally`
block after `app.exec()`. `VshNewsMainWindow.shutdown()` disposes independently
opened module windows, and the smoke test uses the same shutdown path.

## Verification and limitation

- Before the fix, the smoke test passed but its process reproduced exit status
  `0xC0000005`; a direct non-pytest login/show/close run exited normally.
- After the fix, the Qt smoke test passed in 10 consecutive runs with exit status
  `0`. The complete test suite also passed: **28 passed**.
- No crash dump from the user's manual run was available. The teardown failure
  above is reproduced and fixed; if the reported crash occurs during an active
  session rather than on exit, its exact native stack still needs a dump to
  correlate.
