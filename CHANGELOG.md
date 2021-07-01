# Changelog

## 0.0.9 - 2021-07-01

### Added

- Slash commands availaible !

### Changed

- Python 3.8 to Python 3.9

### Fixed

- Minor fixes

## 0.0.8 - 2021-04-15

### Changed

- Improve charts for `c!daily` command which is prettier and more accurate.
- Cooldown command prettier [(#17)](https://github.com/takitsu21/covid-19-tracker/pull/17).

### Fixed

- Fixed minor typos & grammatical errors [(#18)](https://github.com/takitsu21/covid-19-tracker/pull/18)

## 0.0.7 - 2020-04-11

### Added

- `c!setprefix <new_prefix>` You can now set your own guild prefix.
- `@Coronavirus COVID-19 getprefix` Views current guild prefix.

### Fixed

- Fix spelling errors, thanks to [benhovinga](https://github.com/benhovinga) for contributing.

### Changed

- cured to recovered in `c!country` [Issue #8](https://github.com/takitsu21/covid-19-tracker/issues/8)

## 0.0.6 - 2020-04-07

### Added

- `clist` -> list every country that can be call by bot commands.
- **[ISO-3166-1](https://fr.wikipedia.org/wiki/ISO_3166-1)** for all countries

### Fixed

- Improve bot stability.
- Fix minor issues.
- Fix typos.

### Changed

- `c!notification <enable | disable>` -> `c!nofitication <country | disable> <every NUMBER> <hours | days | weeks>` you can have notification about country in a specific channel for your server.
- `c!stats [log]` -> `c!<s | stats> [log | country | log [country]]` you can now have log graph for countries.
- Graph display Total confirmed - active.

## 0.0.5 - 2020-03-29

### Added

- Now with `c!stats <country>` you got a minimap in the right top corner about the selected country.

### Fixed

- Prefix can be interpreted as `C!` and `c!` (useful when you are on mobile).

### Changed

- Back to old format according to your suggestion.

## 0.0.4 - 2020-03-27

### Added

- New emote.
- More information in `c!source`.
- Add Total active cases in `c!stats`

### Fixed

- Fix Notification and tracker.
- Improve data stability.

### Changed

- `c!stats` changed to -> `c!stats [country | log]` and can now show specific graphic for each countries, you can also get the logarithmic graphic.
- change `c!help` for `c!stats`.


## 0.0.3 - 2020-03-17

### Added

- New command : `c!<r | region> <STATE/PROVINCE | all> in <COUNTRY>`,
  now you can get stats from state/province in supported countries
  (**China, Canada, United States, Australia, Cruise Ship**).
- New field in `c!help` for `c!<r | region>` command.
- [Patreon] field added in `c!about`.
- World Health Organization (WHO) source in `c!source`.
- Different formatting on mobile and desktop
- New bot icon

### Fixed

- English typos.

### Changed

- Better formatting visualization for `c!country`, `c!info`, `c!notication`, `c!track`
- Better graphic visualization on x and y axis, timeline rotation and some color changes.
- Embed color

## 0.0.2 - 2020-03-13

### Added

- `c!news` recent news about COVID-19 using newsapi.org
- New field in `c!help` for `c!news`

### Fixed

- Fix typos that didn't match with the current difference visualisation.
- Fix GMT update typos.
- Improvements on data update.

## 0.0.1 - 2020-03-12

### Added

- `c!vote`
- `c!track <COUNTRY | [disabled]>`
- `c!suggestion <MESSAGE>`
- `c!bug <MESSAGE>`
- New data sources.

### Fixed

- Graphical statistics now update the current day cases.
- You can use country code to get a country data with `c!country <COUNTRY>`

[Patreon]: https://www.patreon.com/takitsu