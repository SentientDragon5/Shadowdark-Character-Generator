# Shadowdark Character Generator

A [Shadowdark TTRPG](https://www.thearcanelibrary.com/pages/shadowdark?srsltid=AfmBOoqEC10jtoUg5wPzeaGuIaDnixV_WHS8jxFMCkw1owHMC8o_A2uR) character generator. Written to be modified so that additional classes, ancestries, gear, deities, names, backgrounds... can be edited through code.
The generated characters are by no means perfect, and can and should be modified if used. This project was for if you needed to batch a large amount of random characters.

## Setup

Download the fonts from dafont.com and place them in the font foler.
- [Old NewsPaper](https://www.dafont.com/old-newspaper-font.font) (Free for personal use)
- [JSL Blackletter](https://www.dafont.com/jsl-blackletter.font) (100% Free)
- [Monserrat](https://fonts.google.com/specimen/Montserrat) (Google Fonts)
  - Note: Only put the regular font. The fonts are referenced in the `pdf_print_singles.py` and `pdf_character.py`

Make sure to download Python.
Once this project is cloned, `pip install -r requirements.txt`

## How to Use

Enusre Python is installed. This was built for 3.12, should be compatible with other versions.
```
python --version
> Python 3.12.1
```

There are 2 generation algorithms. `gen_random.py` and `gen_smart.py`. The smart generator will choose the ancestry, class, and gear based off the rolled stats.
Run the generator with:
```
python gen_smart.py
```

The command line argumentsa and help can be found with:
```
python gen_smart.py -h
```

These let you set the level, ancestry, class, or quantity of characters generated.

You can view the pdf in VSCode with an extention like [this](https://marketplace.visualstudio.com/items?itemName=tomoki1207.pdf)

## Credits

Made for Shadowdark, created by Kelsey Dionne
This character generator is an independent tool published under the Shadowdark RPG Third-Party License and is not affiliated with The Arcane Library, LLC. Shadowdark RPG © 2023 The Arcane Library, LLC.

Created by Logan Shehane, with help from Gemini