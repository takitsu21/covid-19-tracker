[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U7U1RSV5)

<a href="https://top.gg/bot/682946560417333283" >
  <img src="https://top.gg/api/widget/status/682946560417333283.svg" alt="Coronavirus COVID-19" />
</a>

[![PyPI pyversions](https://img.shields.io/badge/python-3.8-blue)](https://www.python.org/)  ![AppVeyor](https://img.shields.io/appveyor/ci/takitsu21/WarframeTrader) [![Discord](https://img.shields.io/discord/556268083681951759?color=blue&label=discord)](http://discord.gg/wTxbQYb) ![GitHub pull requests](https://img.shields.io/github/issues-pr/takitsu21/covid-19-tracker) ![GitHub issues](https://img.shields.io/github/issues/takitsu21/covid-19-tracker) [![GitHub](https://img.shields.io/github/license/takitsu21/covid-19-tracker)](LICENCE)
<p align="left"><a href="https://discordbots.org/bot/682946560417333283" >
  <img src="https://top.gg/api/widget/682946560417333283.svg?usernamecolor=FFFFFF&topcolor=000000" alt="Coronavirus COVID-19" />
</a></p>

# Coronavirus COVID-19

This bot gives formatted data about the new Coronavirus COVID-19.

## Commands

Prefix : **`c! or @mention`**

**`<something>`** is required
**`[something]`** is optional
**`arg1 / arg2`** mean arg1 or arg2

| Command | Description |
| ------- | ----------- |
| **`c!help`** | Views help command. |
| **`c!info`** | Views every confirmed cases. |
| **`c!news`** | Views recent news about COVID-19 (update every 1 hour). |
| **`c!stats`** | Views graphical statistics. |
| **`c!country <COUNTRY>`** | Views information about multiple chosen country/region. You can either use autocompletion or country code. Valid country/region are listed in `c!info`. Example : `c!country fr germ it poland`. |
| **`c!track <COUNTRY / [disable]>`** | Track multiple country (bot will DM you update). `c!track <COUNTRY>` work like `c!country <COUNTRY>` (country code / autocompletion) see `c!help`. `c!track disable` will disable the tracker. |
| **`c!notification <enable / disable>`** | (Only administrator) When new datas are downloaded the bot will send you a notification where you typed the command. |
| **`c!source`** | Views source data which the bot is based on. |
| **`c!suggestion <MESSAGE>`** | Send suggestion feedback. |
| **`c!bug <MESSAGE>`** | Send bug feedback. |
| **`c!about`** | Views informations about the bot. |
| **`c!invite`** | Views bot link invite. |
| **`c!vote`** | Views bot vote link. |

## Few examples

![Example info](https://i.imgur.com/jbhAfLp.png)

![Example Stats](https://i.imgur.com/9ik4lg4.png)

![Example country filter](https://i.imgur.com/wt6QNYt.png)

![Example notification](https://i.imgur.com/mTvOfyz.png)

## Built With

* [discord.py]

## Author

* [**takitsu21**]

### License

This project is licensed under the MIT License - see the [LICENSE.md] file for details.

### Deployment

* Scaleway

# [Changelog]

## [0.0.2] - 2020-03-13

### Added

- `c!news` recent news about COVID-19 using newsapi.org
- New field in `c!help` for `c!news`

### Fixed

- Fix typos that didn't match with the current difference visualisation.
- Fix GMT update typos.
- Improvements on data update.

## [0.0.1] - 2020-03-12

### Added

- `c!vote`
- `c!track <COUNTRY | [disabled]>`
- `c!suggestion <MESSAGE>`
- `c!bug <MESSAGE>`
- New data sources.

### Fixed

- Graphical statistics now update the current day cases.
- You can use country code to get a country data with `c!country <COUNTRY>`

[Changelog]: CHANGELOG
[discord.py]: https://discordpy.readthedocs.io/en/latest/
[**takitsu21**]: https://github.com/takitsu21/
[LICENSE.md]: LICENCE