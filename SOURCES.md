# Character artwork

This is an unofficial, personal Five Nights at Freddy's fan profile. FNAF and its characters belong to Scott Cawthon and their respective rights holders. The layout and interface artwork were made for this profile; the character renders and game animation were sourced from the pages below.

| Character / asset | Source page | Download |
| --- | --- | --- |
| Springtrap, full body | [PNG All](https://www.pngall.com/springtrap-png/download/137212/) | [PNG](https://www.pngall.com/wp-content/uploads/15/Springtrap-PNG-HD-Image.png) |
| Springtrap portrait / avatar | [PNG All, Springtrap gallery](https://www.pngall.com/springtrap-png/) | [PNG](https://www.pngall.com/wp-content/uploads/15/Springtrap-PNG-Picture.png) |
| Freddy Fazbear | [PNGAAA](https://www.pngaaa.com/detail/2757370) | [PNG](https://image.pngaaa.com/370/2757370.png) |
| Bonnie | [PNGAAA](https://www.pngaaa.com/detail/4718562) | [PNG](https://image.pngaaa.com/562/4718562.png) |
| Chica | [PNGAAA](https://www.pngaaa.com/detail/2266902) | [PNG](https://image.pngaaa.com/902/2266902.png) |
| Foxy | [PNGAAA](https://www.pngaaa.com/detail/664372) | [PNG](https://image.pngaaa.com/372/664372.png) |
| Original animatronic group | [PNGkey](https://www.pngkey.com/maxpic/u2q8o0o0w7u2i1w7/) | [PNG](https://www.pngkey.com/png/full/158-1584105_clip-art-transparent-fnaf-transparent-1character-five-nights.png) |
| Springtrap camera animation | [GIPHY](https://giphy.com/gifs/NYCjBIBGtyeFq) | [GIF](https://media.giphy.com/media/NYCjBIBGtyeFq/giphy.gif) |

The downloaded character images are compressed as WebP for delivery and embedded in SVG layouts. No character was redrawn or generated. The original square Springtrap portrait is retained as `assets/avatar-springtrap.png`. The GIF is unchanged. Source mirrors do not establish the original artist or an official-render designation; those designations are not asserted here.

# Maintaining the profile

`python3 tools/build_profile.py` rebuilds the SVG layouts from the local assets and saved GitHub snapshot. `python3 tools/build_profile.py --refresh` refreshes the contribution snapshot through the local `gh` CLI first and checks that the authenticated account is `MrTr4p`. It does not publish or push any changes.

Desktop and mobile artwork are selected with `<picture>` elements. All section images include descriptive alternative text, with a native text version available in the README disclosure. The animated camera is inside a separate disclosure.

`profile-settings.json` contains the matching public bio, website, status text, and avatar path. It contains no credentials. GitHub account settings and avatar uploads are separate from the profile README.
