# Build status — v0.1.0-r4

Snapshot: 28 October 2026. R4 is the owner's selected horizontal layout. This is the first CAD-only Wyatt release, not a validated complete DIY device.

| Area | Current evidence | Remaining gate |
| --- | --- | --- |
| Native CAD / STL | Reimported STEP checks and closed-mesh checks are included; frozen geometry is hash-listed. | Same-material coupon and full assembly checks. |
| Original hardware | Espressif original inner-case assets are retained unchanged at a pinned commit. | Fit the actual board revision, occupied connectors and tools using TEST06. |
| Speakers | Design basis: 42 mm rims, different 17/20 mm listed depths; individual fit/retention required. | Stationary frame, cone protrusion/excursion, lead clearance, acoustic test. No matched-pair claim. |
| SEN0428 | Manufacturer 14 × 17 mm PCB outline; internal carrier, rear service cap and ambient path modelled. | Actual board thickness/blank edges/header, seal force, harness entry and detached→installed→detached thermal comparison. |
| Camera | Added R4 geometry leaves the measured original notch and central functional-front envelope clear. | Live corner/framing check on TEST06 and finished shell; no verified lens FOV or photo-storage feature. |
| Printing | Nominal 240 mm main-shell footprint fits a P1S profile envelope with the specified centred brim. | Full slice, supports/exclusions, coupons, real print and desk stability. |
| Firmware / backend | Separate bench development exists; it is not distributed in this CAD release. | Validate and document a reproducible public software build before release. |
| Complete product | Assembled, tested Wyatt units are planned. | Fit, function, production and applicable market requirements; no order or campaign link yet. |

The technical previews show the actual released CAD and a neutral orientation display. They do not show a completed physical product. [Sensor test plan](../hardware/r4/Integrated-sensor-test-plan.txt) and [print-first instructions](../hardware/r4/README-PRINT-FIRST.txt) define the physical checks.

Cloud speech/AI, weather and personal agenda capabilities must be documented with their actual configuration, provider cost, privacy and offline limits in a later software release. No API keys, calendar files, firmware binaries or local runtime settings are included here. A phone Wi-Fi setup flow is not Bluetooth pairing or live calendar synchronization.
