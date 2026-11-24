# The World in One Day — Tuesday 24 November 2026

Entry for the make.fun bounty **news-image-20261124**: sum up 24 November's
world news in one image.

The image is a newspaper front page: a masthead naming the day, a globe with
numbered pins showing where each story happened, one lead story and eight
further stories from 24 November 2026, each verified against reputable
sources (Reuters, BBC, Sydney Morning Herald, Xinhua):

1. Ukraine says it sank a Russian warship off Libya (Benghazi)
2. Solomon Islands to drop its China security pact (Honiara)
3. Sanofi to buy Insmed for $41bn (Paris)
4. Anthropic shares fall below IPO price (New York)
5. Israeli strikes kill at least six in Gaza
6. Iraq moves to take over Kurdish oilfields (Baghdad)
7. Magnitude 5.6 quake shakes eastern Nepal
8. Pakistan astronaut to join China's space station
9. NATO vows to defend space after Russian reports (Brussels)

## How it works

`render.py` draws `entry.png` (1024x1024 PNG) with Python and Pillow.
`main.py` (standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png`, so both grading runs write identical bytes.

Run locally:

```sh
python3 render.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see LICENSE.
