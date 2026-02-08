# Meal plans for university canteens in Bonn

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/alexanderwallau/bonn-mensa/python-publish.yml)
[![PyPI version](https://badge.fury.io/py/bonn-mensa.svg)](https://badge.fury.io/py/bonn-mensa)
[![FlakeHub](https://img.shields.io/endpoint?url=https://flakehub.com/f/alexanderwallau/bonn-mensa/badge)](https://flakehub.com/flake/alexanderwallau/bonn-mensa)

A python script for displaying the meal plans of the canteens of the [Studierendenwerk Bonn](https://www.studierendenwerk-bonn.de/).
The script parses the HTML response of a call to an API.
Depending on your request the API might take a few seconds to respond.

![an example output](images/bonn-mensa_example_output.png)

## Installation

To install this script, run

```sh
 pip install bonn-mensa
```

### MacOS (using homebrew)

To install the application using homebrew, run:

```bash
# Add the tap to homebrew
brew tap alexanderwallau/bonn-mensa https://github.com/alexanderwallau/bonn-mensa

# Install the application
brew install bonn-mensa

# Install the application from main branch
brew install --HEAD bonn-mensa
```

In case you want to remove the application, run:

```bash
brew uninstall bonn-mensa
brew untap alexanderwallau/bonn-mensa
brew autoremove
```

### NixOS (using flakes)

This Repository provides a flake. If you have flakes enabled you can either run

```nix
nix run github:alexanderwallau/bonn-mensa -- <options>
```

for one time use.
If you want to add this to your permanent configuration add

```nix
bonn-mensa = {
      url = "github:alexanderwallau/bonn-mensa";
      inputs = { nixpkgs.follows = "nixpkgs"; };
    };
```

to your flake.nix and adjust the rest of your config accordingly if you are using Home-Manager an example can be found [here](https://github.com/alexanderwallau/nix). One could also use the flakehub route and use

```nix
fh add "alexanderwallau/bonn-mensa/0.1.81"
```

## Usage

To run the script, simply run `mensa`. For a list of all arguments, see `mensa --help`

```bash
$ mensa --help
usage: mensa [-h] [--vegan | --vegetarian]
             [--mensa {SanktAugustin, CAMPO, Hofgarten, FoodtruckRheinbach, VenusbergBistro, CasinoZEF/ZEI, Foodtruck, Rabinstraße}]
             [-- price {Student, Staff, Guest}]
             [--filter-categories [CATEGORY ...]] [--date DATE] [--lang {de,en}] [--show-all-allergens]
             [--show-additives] [--no-colors] [--markdown]
             [--glutenfree] [--pdf]

optional arguments:
  -h, --help            show this help message and exit
  --vegan               Only show vegan options
  --vegetarian          Only show vegetarian options
  --mensa {SanktAugustin,CAMPO,Hofgarten,FoodtruckRheinbach,VenusbergBistro,CasinoZEF/ZEI,Foodtruck, Rabinstraße, Rheinbach}
                        The canteen to query. Defaults to CAMPO.
  --price {Student, Staff, Guest}
          The price to display on output defaults to Student
  --filter-categories [CATEGORY ...]
                        Meal categories to hide. Defaults to ['Buffet', 'Dessert'].
  --date DATE           The date to query for in YYYY-MM-DD format. Defaults to today.
  --lang {de,en}        The language of the meal plan to query. Defaults to German.
  --show-all-allergens  Show all allergens. By default, only allergens relevant to vegans (e.g. milk or fish) are shown.
  --show-additives      Show additives.
  --glutenfree          Show only gluten free meals
  --no-colors           Do not use any ANSI colors in the output.
  --markdown            Output in markdown table format.
  --pdf                 Download the meal plan of the current week for specified canteen as a PDF.
  --verbose             Output Debug Log
```
