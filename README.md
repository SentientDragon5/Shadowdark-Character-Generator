# Shadowdark Character Generator

A [Shadowdark TTRPG](https://www.thearcanelibrary.com/pages/shadowdark?srsltid=AfmBOoqEC10jtoUg5wPzeaGuIaDnixV_WHS8jxFMCkw1owHMC8o_A2uR) character generator. Written to be modified so that additional classes, ancestries, gear, deities, names, backgrounds... can be edited through code.
The generated characters are by no means perfect, and can and should be modified if used. This project was for if you needed to batch a large amount of random characters.

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

## Credits

Made for Shadowdark, created by Kelsey Dionne
This character generator is an independent tool published under the Shadowdark RPG Third-Party License and is not affiliated with The Arcane Library, LLC. Shadowdark RPG © 2023 The Arcane Library, LLC.

Created by Logan Shehane, with help from Gemini