# Night-shift profile

The profile uses original, self-contained SVG artwork: a CCTV floor plan, moving camera selection, system checks, project diagrams, and animated contribution charts. It contains no raster character images, external fonts, JavaScript, or remote image-generation services.

The visual direction takes its cues from FNAF security and maintenance interfaces. The reference profile was [darkyeg](https://github.com/darkyeg), whose current README uses animated SVG cards and responsive dark/light variants. Its artwork and personal content were not copied.

## Interactions

- Navigation links jump to camera feeds, maintenance, the security log, and contact links.
- Project cards open their corresponding repositories.
- Native README disclosures open the personnel file, additional feeds, maintenance systems, and exact activity values. They work with mouse, touch, and keyboard.
- The camera map, route indicators, system bars, and chart entrances use SVG CSS animations. Reduced motion disables the animations and shows the first camera.
- The footer returns to the top of the page.

The decorative camera animation cycles automatically. It does not imply a visitor-operated camera game. README images cannot execute application JavaScript or receive click events on their internal graphics.

## Data

The activity snapshot uses the same **public** contribution calendar available at [MrTr4p's public calendar](https://github.com/users/MrTr4p/contributions). Repository metadata comes from the public repositories queried through the locally authenticated GitHub CLI. The saved snapshot includes its period and public visibility. Private contribution data is not included.

The contribution total, active days, and longest streak use the displayed calendar period; they are not lifetime totals. Each monthly bucket includes only dates within that period. Exact values are available in the README's activity disclosure.

## Build

Run `python3 tools/build_profile.py` to rebuild the graphics and README from `assets/profile-data.json`.

Run `python3 tools/build_profile.py --refresh` to update public data first. Refresh verifies that the local `gh` account is `MrTr4p`. The script does not commit, push, or change account settings.

There are desktop/mobile and dark/light variants for every panel. All fonts are rendered as SVG text; all diagrams and charts are vectors. Alternative text identifies each linked panel and its function.
