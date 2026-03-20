---
name: mensa-today
description: Fetches today's Mensa meal plans with the `mensa` CLI. Remembers dietary preferences, preferred Mensa, and preferred price class.
---

# Mensa Today (portable)

Use this skill when the user wants today's meal plan from a Bonn canteen. The skill stores dietary preferences plus the user's preferred Mensa and price class in a generic location.

## What this uses

This skill invokes the **`mensa` CLI**.

## Basic workflow (portable version)

1. **Pick the date** – use today’s date, but if the current time is after 15:00 or it’s a weekend, bump to the next workday.
2. **Select the canteen** –
   * Read `~/.config/mensa/preferences.json` (if it exists).
   * If the user explicitly mentions a canteen in the current request, use that canteen and persist it to the config file.
   * Otherwise, if the file contains a stored canteen (for example `{"mensa": "Hofgarten"}`), use that.
   * If no canteen is stored, default to `CAMPO`.
3. **Determine dietary filter** –
   * Read `~/.config/mensa/preferences.json` (if it exists).
   * If the file contains `{"vegan": true}` → add `--vegan`.
   * Else if it contains `{"vegetarian": true}` → add `--vegetarian`.
   * If no preference is set → **no** dietary flag (full menu).
4. **Determine price class** –
   * Read `~/.config/mensa/preferences.json` (if it exists).
   * If the user explicitly mentions a price class in the current request, use it and persist it to the config file.
   * Otherwise, if the file contains a stored price class (for example `{"price": "Guest"}`), use that.
   * If no price class is stored, default to `Student`.
5. **Language** – always add `--lang de` so dish names stay in German.
6. **Locate the `mensa` binary** –
   * Prefer the path in the environment variable `MENSA_BIN` if set.
   * Otherwise rely on `which mensa` (standard `$PATH`).
   * If no binary is found, report an error to the user.
7. **Build the command line** using the pieces above. Append `--markdown` when a compact output is requested.
8. **Run the command** and capture its output.
9. **Post‑process** – if any dish mentions *Pommes*, *Fries* or *Fritten*, prepend a note that fries are present.
10. **Summarize** – present canteen name, date, the list of dishes, the price category, and the fries note (if applicable).

## Important defaults from the CLI

- default canteen: stored `mensa` from config, otherwise `CAMPO`
- default price class: stored `price` from config, otherwise `Student`
- default date: today when `--date` is omitted
- useful filters: `--vegan`, `--vegetarian`, `--glutenfree`
- useful output format: `--markdown`

## Common commands (examples)

Show today’s meals for CAMPO (full list):

```bash
mensa --date "$(date +%F)" --mensa CAMPO --price Student --lang de
```

Show today’s meals for CAMPO in markdown (compact):

```bash
mensa --date "$(date +%F)" --mensa CAMPO --price Student --lang de --markdown
```

Vegetarian meals only (if preference set):

```bash
mensa --date "$(date +%F)" --mensa CAMPO --vegetarian --price Student --lang de
```

Vegan meals only (if preference set):

```bash
mensa --date "$(date +%F)" --mensa CAMPO --vegan --price Student --lang de
```

Gluten‑free meals only:

```bash
mensa --date "$(date +%F)" --mensa CAMPO --glutenfree --price Student --lang de
```

## Canteen names supported by the CLI

- `CAMPO`
- `SanktAugustin`
- `Hofgarten`
- `FoodtruckRheinbach`
- `VenusbergBistro`
- `CasinoZEF/ZEI`
- `Foodtruck`
- `Rabinstraße`
- `Rheinbach`

## Interaction rules (portable & preference‑aware)

- If the user says **"mensa"** → use the stored preferred Mensa if available, otherwise assume `CAMPO`.
- If the user mentions a specific canteen → use that.
- If the user mentions a specific canteen and it differs from the stored one, update `~/.config/mensa/preferences.json` so future requests reuse that Mensa.
- If the user mentions a specific price class such as `Student`, `Staff`, or `Guest`, use it and update `~/.config/mensa/preferences.json` so future requests reuse that price class.
- **Vegetarian / Vegan handling** – the skill respects the persistent preference file:
  * When a user says *"I’m vegetarian"* the assistant writes `{"vegetarian": true}` to `~/.config/mensa/preferences.json`.
  * When a user says *"I’m vegan"* it writes `{"vegan": true}` (overrides any vegetarian flag).
  * When a user says *"I’m not vegetarian"* or *"I’m not vegan"* the corresponding key is set to `false`.
  * If the file does not exist, the CLI is called **without** any dietary flag (full menu).
- If the user explicitly requests a diet in the current request (e.g., *"show me vegan meals"*), that flag overrides whatever is stored.
- The assistant can reset the preference on request (e.g., *"forget my diet"* → the file is cleared).
- If the user wants a quick answer, the skill prefers `--markdown`.
- If no price class is mentioned in the request, the skill uses the stored `price` value if available, otherwise `Student`.
- If the command fails (binary missing, network error, etc.) the assistant reports that the meal plan may be unavailable for that canteen/date.

## Output style

Keep the response concise:
- canteen name
- date
- listed dishes
- price category if shown
- explicitly mention any fries / Pommes
- dietary tags or allergens only if the user asked for them

## User Preference handling (generic location)

The skill reads and writes a tiny JSON file to remember dietary choices, the preferred Mensa, and the preferred price class.

**Path:** `~/.config/mensa/preferences.json`

**Structure example:**
```json
{
  "mensa": "CAMPO",
  "price": "Student",
  "vegetarian": true,
  "vegan": false
}
```

When a user states a diet, the assistant updates this file accordingly. When a user explicitly selects a different Mensa, the assistant also updates the `mensa` field. When a user explicitly selects a different price class, the assistant updates the `price` field. When the user says *"reset my diet"* the file is cleared (or the relevant keys are set to `false`).
