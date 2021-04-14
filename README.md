[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U7U1RSV5)

<a href="https://top.gg/bot/682946560417333283" >
  <img src="https://top.gg/api/widget/status/682946560417333283.svg" alt="Coronavirus COVID-19" />
</a>

[![PyPI pyversions](https://img.shields.io/badge/python-3.8-blue)](https://www.python.org/)  ![AppVeyor](https://img.shields.io/appveyor/ci/takitsu21/WarframeTrader) [![Discord](https://img.shields.io/discord/556268083681951759?color=blue&label=discord)](http://discord.gg/wTxbQYb) ![GitHub pull requests](https://img.shields.io/github/issues-pr/takitsu21/covid-19-tracker) ![GitHub issues](https://img.shields.io/github/issues/takitsu21/covid-19-tracker) [![GitHub](https://img.shields.io/github/license/takitsu21/covid-19-tracker)](LICENCE)
<p align="left"><a href="https://discordbots.org/bot/682946560417333283" >
  <img src="https://top.gg/api/widget/682946560417333283.svg?usernamecolor=FFFFFF&topcolor=000000" alt="Coronavirus COVID-19" />
</a></p>

# Coronavirus COVID-19

Get the latest update with notification alerts and graphics stats about COVID-19! For every country and region! World news are available too!

## Commands

Prefix : **`c! or @mention`**

**`<something>`** is required
**`[something]`** is optional
**`arg1 / arg2`** mean arg1 or arg2

| Command | Description |
|-------|-----------|
| **`c!help`** | Displays help command. |
| **`c!info`** | Displays every confirmed case. |
| **`c!list`** | List every country affected by COVID-19 |
| **`c!<s / stats> [log / country / log [country]]`** | Displays graphical statistics. If no args provided return linear graph for total cases. You can find countries with **full name** or **[ISO-3166-1](https://fr.wikipedia.org/wiki/ISO_3166-1)**.__Examples__ : `c!stats us`, `c!s log usa`, `c!stats log` |
| **`c!<r / region> <state/province / all> in <country>`** | Supported countries (**China, Canada, United States, Australia, Cruise Ship**). Displays regions infected within a  country or in the whole state with the `all` arg. The `in` (mandatory symbol) is interpreted as separator between the country and the region/province so don't forget it. Example 1 : `c!r new york in us`. Example 2 : `c!region all in china`. |
| **`c!track <country / [disable]>`** | Track country (bot will DM you update). __Examples__ : `c!track us`, `c!track disable`. |
| **`c!news`** | Views recent news about COVID-19 (update every 1 hour). |
| **`c!notification <country / disable> <every NUMBER> <hours / days / weeks>`** | (Only administrator) When new data is found, the bot will send you a notification where you executed the command, **server only**. __Examples__ : `c!notification usa every 3 hours`, `c!notification disable` |
| **`c!source`** | Displays source data which the bot is based on. |
| **`c!suggestion <message>`** | Send suggestion feedback. |
| **`c!bug <message>`** | Send bug feedback. |
| **`c!about`** | Displays information about the bot. |
| **`c!invite`** | Displays bot link invite. |
| **`c!vote`** | Displays bot vote link. |

## Few examples

- `c!s us`

![Example Stats](https://i.imgur.com/mykjbCr.png)

- `c!s log`

![Stats log](https://i.imgur.com/XKKXRE2.png)

- `c!notif usa every 2 hours`

![Example notification](https://i.imgur.com/TJOUp00.png)

- `c!region all in us`

![State/Province](https://i.imgur.com/4L4R0FZ.png)

- `c!info`

![Example info](https://i.imgur.com/LIIoU2O.png)

## Built With

* [discord.py]

## Author

* [**takitsu21**]

### License

This project is licensed under the MIT License - see the [LICENSE.md] file for details.

### Deployment

* Scaleway

# Changelog

## 0.0.7 - 2021-04-07

### Fixed

- Fixed minor typos
- Fixed minor grammatical errors

## 0.0.6 - 2020-04-07

### Added

- `c!list` -> list every country that can be called by bot commands.
- **[ISO-3166-1](https://fr.wikipedia.org/wiki/ISO_3166-1)** for all countries

### Fixed

- Improve bot stability.
- Fixed minor issues.
- Fixed typos.

### Changed

- `c!notification <enable | disable>` -> `c!nofitication <country | disable> <every NUMBER> <hours | days | weeks>` you can have a notification about a country in a specific channel of your server.
- `c!stats [log]` -> `c!<s | stats> [log | country | log [country]]` you can now have a log graph for countries.

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
- More informations in `c!source`.
- Add Total active cases in `c!stats`

### Fixed

- Fix Notification and tracker.
- Improve data stability.

### Changed

- `c!stats` changed to -> `c!stats [country | log]` and can now show specific graphic for each countries, you can also
  get the logarithmic graphic.
- change `c!help` for `c!stats`.

## 0.0.3 - 2020-03-17

### Added

- New command : `c!<r | region> <STATE/PROVINCE | all> in <COUNTRY>`, now you can get stats from state/province in
  supported countries
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

[Changelog]: CHANGELOG

[discord.py]: https://discordpy.readthedocs.io/en/latest/

[**takitsu21**]: https://github.com/takitsu21/

[LICENSE.md]: LICENCE

