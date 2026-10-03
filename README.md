# duckyPad Pro + INIU P781 case — v0.1

Parametric 3D-printable enclosure for a **duckyPad Pro** with an **INIU SnapGo Air P781 10,000 mAh** power bank hidden underneath.

## Design targets

- 6.5° typing angle to match the Ikki68 Aurora R2.
- 22.86 mm (0.9 in) default front body height; this is a parameter in the source and can be changed after comparing directly to your Ikki68.
- 112 mm case depth, approximately matching the Ikki68's 4.4 in depth.
- Rear-loading INIU P781 battery bay.
- Full rear I/O bay exposes the P781 display and both USB-C ports.
- A taller rear notch gives room for a U-shaped USB-C adapter to reach the duckyPad's upper/power USB-C port.
- Right-side tunnel preserves access to the duckyPad's second USB-C port.
- Uses official duckyPad Pro PCB outline / mounting-hole coordinates from the open-source Eagle board file.

## Included files

- `duckypad_case_body.step` — editable solid.
- `duckypad_case_body.stl` — full case, ready for slicing.
- `rear_fit_test.step` / `.stl` — only the rear 20 mm of the enclosure. **Print this first.**
- `optional_battery_lip.step` / `.stl` — low removable/friction-fit lip that helps prevent the bank from sliding out. The U-adapter itself will also retain the bank.
- `assembly_preview.step` — case + nominal PCB + nominal P781 envelope + approximate original top plate. Reference only; do not print as one part.
- `active_mounts.txt` — which official PCB M2 mounting holes are used by this battery placement.
- `duckypad_ikki_powerbank_case.py` — CadQuery source. Change dimensions here and rerun to regenerate STEP/STL files.

## Important v0.1 assumptions

### INIU P781
Nominal body envelope used:

- 105.0 mm long
- 71.0 mm wide
- 13.7 mm thick
- pocket adds 0.8 mm total clearance in X and Y

The P781 slides into the case from the rear. Its short edge containing the display/USB-C ports is left visible through the rear opening.

Because product photos do not give trustworthy USB-C center-to-center measurements, the model intentionally exposes the entire port/display edge rather than creating tight individual cutouts.

### duckyPad Pro
The source uses the official board geometry:

- PCB outline: 109 x 96 mm
- rounded PCB corners: 3.5 mm radius
- board is mounted at the same 6.5° angle as the enclosure
- 8 M2 mounting locations are retained on the left side; a sloped support rail supports the right edge while leaving the lower/right USB-C area open

The PCB mounting posts currently contain **3.2 mm diameter x 4 mm deep pockets** intended for small M2 heat-set inserts. Adjust `POST_PILOT_D` and `POST_PILOT_DEPTH` in the source if your inserts differ.

## Suggested assembly

1. Print `rear_fit_test.stl` first.
2. Verify the P781 slides in cleanly and the rear display/ports are where you want them.
3. Check your chosen U-shaped USB-C adapter against the rear opening.
4. Print the full body.
5. Install M2 heat-set inserts in the eight active PCB posts.
6. Build the duckyPad PCB/top-plate stack. You may need longer M2 screws or male/female M2 standoffs for the case-mounted holes instead of the original bottom-plate hardware.
7. Screw the PCB assembly to the case posts.
8. Slide the P781 in from the rear.
9. Fit the optional low retaining lip if needed.
10. Connect the bank to the duckyPad's **upper USB-C** power port.

## Parameters most likely to change after the first test print

In `duckypad_ikki_powerbank_case.py`:

- `FRONT_BODY_H` — change this if your physical Ikki68 measurement differs from 22.86 mm.
- `PB_X` — shifts the battery left/right to align one P781 USB-C port with your U-adapter.
- `PB_Y` — moves the power bank fore/aft.
- `PB_CLEAR_X`, `PB_CLEAR_Y` — tune for your printer/material.
- `UPPER_USB_CHIMNEY_W` — increase for a wider U-adapter.
- `POST_PILOT_D`, `POST_PILOT_DEPTH` — match your heat-set inserts.

## Printing notes

Prototype recommendation:

- PETG or PLA+ for v0.1.
- 0.20 mm layers are fine for the full case; 0.16 mm if you care about the visible walls.
- 4 perimeters / walls.
- 20–30% infill is sufficient; most strength comes from the shell.
- Print the full case desk-side-down.
- The large top opening and rear I/O opening are intended to minimize support material.

## Sources used for design dimensions

- duckyPad Pro open-source hardware: https://github.com/dekuNukem/duckyPad-Pro
- community duckyPad case / assembly reference: https://github.com/msetsma/ducky-pad-pro
- INIU P781 specifications: https://iniushop.com/products/iniu-p781-qi2-2-magnetic-power-bank
- Ikki68 Aurora R2 specifications: typing angle 6.5°, base height 0.9 in, depth 4.4 in.

## Status

This is a **first printable prototype**, not a physically test-fitted production revision. The solid models have been checked for watertightness and the nominal P781/PCB reference solids do not intersect the enclosure. The remaining unknown is the real-world USB-C/U-adapter alignment, which is why the battery position and rear opening are intentionally parametric/generous.